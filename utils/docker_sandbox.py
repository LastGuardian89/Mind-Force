import docker
from docker.errors import DockerException
from .exceptions import DockerSecurityException, ResourceLimitExceeded, CodeExecutionError

class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self._validate_docker()
        
    def _validate_docker(self):
        try:
            self.client.ping()
        except DockerException:
            raise RuntimeError("Docker daemon not available")

    async def execute(self, code: str, timeout=10, mem_limit='100m') -> str:
        self._check_code_safety(code)
        
        try:
            container = self.client.containers.run(
                image="python-sandbox:secure",
                command=f"timeout -s KILL {timeout} python -c '{code}'",
                mem_limit=mem_limit,
                network_mode="none",
                pids_limit=100,
                read_only=True,
                detach=True
            )
            
            try:
                result = container.wait(timeout=timeout + 2)
                if result['StatusCode'] != 0:
                    raise CodeExecutionError(f"Exit code {result['StatusCode']}")
                    
                logs = container.logs().decode()
                self._check_output_safety(logs)
                return logs
                
            except docker.errors.ContainerError as e:
                raise CodeExecutionError(str(e))
            finally:
                container.remove(force=True)
                
        except docker.errors.ImageNotFound:
            raise CodeExecutionError("Sandbox image not found")
        except Exception as e:
            raise CodeExecutionError(str(e))

    def _check_code_safety(self, code: str):
        dangerous_patterns = [
            'os.system', 'subprocess', 'open(',
            'import socket', 'import shutil',
            '__import__', 'eval(', 'exec('
        ]
        
        if any(pattern in code for pattern in dangerous_patterns):
            raise DockerSecurityException(code)

    def _check_output_safety(self, output: str):
        if len(output) > 10_000:
            raise ResourceLimitExceeded("Output size")