export function messageListTemplate() {
  return `
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4" x-ref="messages">

      <template x-for="(msg, i) in messages" :key="i">
        <div class="msg-enter" :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
          <div class="chat-bubble"
               :class="msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant'"
               x-text="msg.text">
          </div>
        </div>
      </template>

      <template x-if="loading">
        <div class="flex justify-start msg-enter">
          <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm min-w-[220px]">
            <div class="flex items-center gap-2">
              <div class="flex gap-1.5">
                <span class="chat-loader-dot" style="animation-delay:0ms"></span>
                <span class="chat-loader-dot" style="animation-delay:150ms"></span>
                <span class="chat-loader-dot" style="animation-delay:300ms"></span>
              </div>
              <span class="text-xs text-gray-400" x-text="elapsed + ' / ~' + (estimate || '?') + ' сек'"></span>
            </div>
            <p class="text-xs text-gray-500 mt-1" x-text="status"></p>
          </div>
        </div>
      </template>

      <template x-if="lastLogs.length > 0 && !loading">
        <div class="flex justify-start">
          <div class="w-full max-w-[85%]">
            <button @click="showLogs = !showLogs"
                    class="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 mb-1">
              <svg class="w-3 h-3 transition-transform" :class="showLogs && 'rotate-90'"
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
              Логи обработки
            </button>
            <div x-show="showLogs" x-transition
                 class="bg-gray-900 text-green-400 text-xs font-mono rounded-lg p-3 overflow-x-auto">
              <template x-for="(log, j) in lastLogs" :key="j">
                <div x-text="log" class="py-0.5"></div>
              </template>
            </div>
          </div>
        </div>
      </template>

    </div>`;
}
