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
          <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm min-w-[260px]">
            <div class="flex items-center gap-2 mb-2">
              <div class="flex gap-1.5">
                <span class="chat-loader-dot" style="animation-delay:0ms"></span>
                <span class="chat-loader-dot" style="animation-delay:150ms"></span>
                <span class="chat-loader-dot" style="animation-delay:300ms"></span>
              </div>
              <span class="text-xs font-medium"
                    :class="complexity === 'easy' ? 'text-green-500' : complexity === 'hard' ? 'text-orange-500' : 'text-blue-500'"
                    x-text="waitLabel"></span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5 mb-2" x-show="estimate > 0">
              <div class="h-1.5 rounded-full transition-all duration-1000"
                   :class="complexity === 'easy' ? 'bg-green-400' : complexity === 'hard' ? 'bg-orange-400' : 'bg-blue-400'"
                   :style="'width:' + Math.min((elapsed / (estimate || 1)) * 100, 95) + '%'">
              </div>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-xs text-gray-500 truncate max-w-[180px]" x-text="status"></p>
              <span class="text-xs text-gray-400" x-text="elapsed + ' сек'"></span>
            </div>
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
