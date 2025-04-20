class SecurityException(Exception):
    def __init__(self, message="Security violation detectted"):
        super().__init__(message)

class InjectionAttemptError(SecurityException):
    def __init__(self, pattern):
        super().__init__(f"Potential injection attempt detect: {pattern}")
    
class DockerSecurityException(SecurityException):
    def __init__(self, code_snippet):
        super().__init__(f"Dangerous code blocked: {code_snippet}")

class ProcessingError(Exception):
    """Base class for processing errors"""
    def __init__(self, message="Processing failed"):
        super().__init__(message)

class PDFProcessingError(ProcessingError):
    """PDF-related errors"""
    def __init__(self, reason):
        super().__init__(f"PDF processing failed: {reason}")

class CodeExecutionError(ProcessingError):
    """Code execution errors"""
    def __init__(self, reason):
        super().__init__(f"Code execution failed: {reason}")

class ResourceLimitExceeded(ProcessingError):
    """Resource limitation errors"""
    def __init__(self, resource_type):
        super().__init__(f"{resource_type} limit exceeded")

class NetworkError(ProcessingError):
    """Network-related errors"""
    def __init__(self, url):
        super().__init__(f"Network operation failed for: {url}")