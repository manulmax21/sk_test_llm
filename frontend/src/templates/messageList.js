import { welcomeTemplate } from "./welcome.js";

export function messageListTemplate() {
  return `
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4" x-ref="messages">

      ${welcomeTemplate()}

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
          <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <div class="flex gap-1.5">
              <span class="chat-loader-dot" style="animation-delay:0ms"></span>
              <span class="chat-loader-dot" style="animation-delay:150ms"></span>
              <span class="chat-loader-dot" style="animation-delay:300ms"></span>
            </div>
          </div>
        </div>
      </template>

    </div>`;
}
