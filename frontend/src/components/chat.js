import { sendQuestionStream } from "../api/client.js";

const WELCOME_MESSAGE =
  "Здравствуйте! Я — менеджер компании по банкротству физических лиц. " +
  "Если у вас есть долги, которые стало сложно выплачивать, — расскажите " +
  "коротко о вашей ситуации, и я подскажу, чем мы можем помочь. " +
  "Консультация бесплатная и ни к чему не обязывает.";

const COMPLEXITY_LABELS = {
  easy: "Простой вопрос",
  medium: "Вопрос средней сложности",
  hard: "Сложный вопрос",
};

export function chat() {
  return {
    messages: [{ role: "assistant", text: WELCOME_MESSAGE }],
    input: "",
    loading: false,
    error: "",
    elapsed: 0,
    estimate: 0,
    complexity: "",
    status: "",
    lastLogs: [],
    showLogs: false,
    sessionId: "",
    _timer: null,

    get waitLabel() {
      const label = COMPLEXITY_LABELS[this.complexity] || "";
      const est = this.estimate;
      if (!est) return label || "Обработка...";

      const timeStr = est < 60
        ? `около ${est} секунд`
        : `около ${Math.ceil(est / 60)} минут`;

      return label
        ? `${label} — ожидание ${timeStr}`
        : `Ожидание ${timeStr}`;
    },

    async send() {
      const text = this.input.trim();
      if (!text || this.loading) return;

      this.messages.push({ role: "user", text });
      this.input = "";
      this.error = "";
      this.status = "Подключение...";
      this.loading = true;
      this.elapsed = 0;
      this.estimate = 0;
      this.complexity = "";
      this.lastLogs = [];
      this.showLogs = false;
      this.scrollDown();

      this._timer = setInterval(() => { this.elapsed++; }, 1000);

      try {
        const result = await sendQuestionStream(text, {
          onStatus: (s) => { this.status = s; },
          onEstimate: (info) => {
            this.estimate = info.seconds || 0;
            this.complexity = info.complexity || "";
          },
          onSession: (id) => { this.sessionId = id; },
          sessionId: this.sessionId,
        });
        this.messages.push({ role: "assistant", text: result.answer });
        this.lastLogs = result.logs;
      } catch (e) {
        this.error = e.message || "Не удалось получить ответ";
      } finally {
        clearInterval(this._timer);
        this._timer = null;
        this.loading = false;
        this.status = "";
        this.scrollDown();
        this.$nextTick(() => this.$refs.input?.focus());
      }
    },

    scrollDown() {
      this.$nextTick(() => {
        const el = this.$refs.messages;
        if (el) el.scrollTop = el.scrollHeight;
      });
    },
  };
}
