import { sendQuestion } from "../api/client.js";

const WELCOME_MESSAGE =
  "Здравствуйте! Я — ассистент контакт-центра. " +
  "Задайте вопрос по теме банкротства или юриспруденции, и я постараюсь помочь.";

export function chat() {
  return {
    messages: [{ role: "assistant", text: WELCOME_MESSAGE }],
    input: "",
    loading: false,
    error: "",
    elapsed: 0,
    _timer: null,

    async send() {
      const text = this.input.trim();
      if (!text || this.loading) return;

      this.messages.push({ role: "user", text });
      this.input = "";
      this.error = "";
      this.loading = true;
      this.elapsed = 0;
      this.scrollDown();

      this._timer = setInterval(() => { this.elapsed++; }, 1000);

      try {
        const answer = await sendQuestion(text);
        this.messages.push({ role: "assistant", text: answer });
      } catch (e) {
        this.error = e.message || "Не удалось получить ответ";
      } finally {
        clearInterval(this._timer);
        this._timer = null;
        this.loading = false;
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
