import Alpine from "alpinejs";
import "./styles/main.css";

import { chat } from "./components/chat.js";
import { renderApp } from "./app.js";

Alpine.data("chat", chat);

renderApp(document.getElementById("app"));

Alpine.start();
