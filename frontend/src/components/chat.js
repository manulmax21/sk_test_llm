import { sendQuestion } from "../api/client.js";

export function chat() {
  return {
    messages: [],
    input: "",
    loading: false,
    error: "",

    async send() {
      const text = this.input.trim();
      if (!text || this.loading) return;

      this.messages.push({ role: "user", text });
      this.input = "";
      this.error = "";
      this.loading = true;
      this.scrollDown();

      try {
        const answer = await sendQuestion(text);
        this.messages.push({ role: "assistant", text: answer });
      } catch (e) {
        this.error = e.message || "Не удалось получить ответ";
      } finally {
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
