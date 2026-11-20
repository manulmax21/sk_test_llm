export function chatInputTemplate() {
  return `
    <div x-show="error" x-transition
         class="mx-4 mb-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
      <span x-text="error"></span>
      <button @click="error=''" class="ml-2 font-medium hover:underline">Закрыть</button>
    </div>

    <div class="bg-white border-t px-4 py-3 shrink-0">
      <form @submit.prevent="send" class="flex gap-2">
        <input
          x-model="input"
          :disabled="loading"
          type="text"
          placeholder="Введите вопрос..."
          class="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm
                 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
                 disabled:opacity-50"
          x-ref="input"
        >
        <button
          type="submit"
          :disabled="loading || !input.trim()"
          class="bg-brand-600 text-white rounded-xl px-4 py-2.5 text-sm font-medium
                 hover:bg-brand-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </form>
    </div>`;
}
