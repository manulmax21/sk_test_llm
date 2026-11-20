const title = import.meta.env.VITE_APP_TITLE || "Ассистент";
const subtitle = import.meta.env.VITE_APP_SUBTITLE || "";

export function headerTemplate() {
  return `
    <header class="bg-white border-b px-4 py-3 flex items-center gap-3 shrink-0">
      <div class="w-10 h-10 rounded-full bg-brand-600 flex items-center justify-center">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
        </svg>
      </div>
      <div>
        <h1 class="font-semibold text-gray-900">${title}</h1>
        <p class="text-xs text-gray-500">${subtitle}</p>
      </div>
    </header>`;
}
