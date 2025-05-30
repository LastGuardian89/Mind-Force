# 🧠 MindForсe: Intelligent Context-Aware Assistant [beta-version]

**Умный ассистент с поддержкой контекста, анализом документов и безопасным выполнением кода**

---

## 🌟 Особенности

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
