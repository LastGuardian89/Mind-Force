# 🧠 MindForge: Intelligent Context-Aware Assistant

<img src="assets/logo.png" width="150" align="right">

**Умный ассистент с поддержкой контекста, анализом документов и безопасным выполнением кода**

---

## 🌟 Особенности

<div align="center">
  <img src="assets/features.png" width="800">
</div>

- 📄 **Анализ PDF** (по ссылкам и локальным файлам)
- ⌨️ **Безопасное выполнение кода** в Docker-песочнице
- 🤖 **Итеративное улучшение ответов** (Society of Mind)
- 🔒 **Защита от инъекций** с помощью BERT-модели
- 🧩 **Модульная архитектура** с переиспользуемыми агентами
- ⚡ **Умное кэширование** с учетом версий и данных

---

## 🏗 Архитектура системы

```mermaid
graph TD
    A[Пользовательский запрос] --> B{Тип контента}
    B -->|PDF-ссылка| C[PDFLinkAgent]
    B -->|Код| D[CodeExecutionAgent]
    B -->|Локальный PDF| E[PDFFileAgent]
    B -->|Текст| F[DefaultAgent]
    C --> G[Извлечение текста]
    D --> H[Запуск в Docker]
    E --> G
    G --> I[Семантический поиск]
    H --> J[Сбор результатов]
    I --> K[Society of Mind]
    J --> K
    K --> L[Генерация ответа]
    L --> M[Кэширование]
    M --> N[Пользователь]


🚀 Быстрый старт
Установка
bash
git clone https://github.com/yourusername/mindforge.git
cd mindforge
pip install -r requirements.txt
docker-compose up --build
Пример использования
python
from mindforge import MindForge

assistant = MindForge()

# Анализ PDF по ссылке
response = assistant.ask(
    "Объясни результаты из отчета: https://example.com/report.pdf"
)

# Выполнение кода
result = assistant.ask(
    "Что делает этот код?",
    code="print('Hello World')"
)

print(response)
🧩 Компоненты системы
<div align="center"> <img src="assets/agents.png" width="600"> </div>
Агент	Описание
PDFLinkAgent	Анализ PDF по URL
PDFFileAgent	Обработка локальных PDF
CodeExecutionAgent	Безопасный запуск кода
DefaultAgent	Базовая текстовая генерация
🛠 Технологический стек
<div align="center"> <img src="assets/tech-stack.png" width="600"> </div>
Ядро: Python 3.10+

ML: Transformers, Sentence-BERT

Безопасность: Docker Sandboxing

PDF: PyMuPDF, PDFPlumber

Кэширование: Redis

Инфраструктура: Docker, RabbitMQ



pie
    title Время обработки запросов
    "PDF Analysis" : 45
    "Code Execution" : 30
    "Text Generation" : 25
