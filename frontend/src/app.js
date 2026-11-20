import { headerTemplate } from "./templates/header.js";
import { messageListTemplate } from "./templates/messageList.js";
import { chatInputTemplate } from "./templates/chatInput.js";

export function renderApp(root) {
  root.innerHTML = `
    <div x-data="chat" x-cloak class="max-w-2xl mx-auto flex flex-col h-screen">
      ${headerTemplate()}
      ${messageListTemplate()}
      ${chatInputTemplate()}
    </div>`;
}
