document.addEventListener("DOMContentLoaded", function () {
    if (window.WasmModule && window.WasmModule.init) {
        window.WasmModule.init().then(() => {
            setupHandlers();
        }).catch((err) => {
            console.error("WASM init failed:", err);
        });
    } else {
        console.error("WASM Module not found");
    }
});

function setupHandlers() {
    const cipherForm = document.getElementById("cipher-form");
    const tokenForm = document.getElementById("token-form");
    const messageForm = document.getElementById("message-form");

    const tokenInput = document.getElementById("token-input");
    const tokenBtn = document.getElementById("set-token-btn");

    const msgInput = document.getElementById("message-input");
    const msgBtn = document.getElementById("send-msg-btn");

    cipherForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const senderCLI = document.getElementById("sender-cli");
        senderCLI.innerHTML = "";

        appendCliLine("sender-cli","> Sending cipher config to host...");
        appendCliLine("sender-cli","");

        fetch("/set-cipher", {
            method: "POST",
            body: new FormData(cipherForm)
        })
        .then((response) => response.json())
        .then((data) => {
            const receiverCLI = document.getElementById("receiver-cli");
            receiverCLI.innerHTML = "";

            data.receiver_log.forEach(line => {
                appendCliLine("receiver-cli", line);
            });

            // Enable next step
            tokenInput.disabled = false;
            tokenBtn.disabled = false;
        });
    });

    tokenForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const token = tokenInput.value;

        // 1. WASM-generiertes Noise Field im Sender-Terminal anzeigen
        const wasmNoise = window.WasmModule.generate_noise_field(token, 10, 0.1);
        const senderNoiseText = wasmNoise
            .reduce((lines, val, idx) => {
                const row = Math.floor(idx / 10);
                if (!lines[row]) lines[row] = [];
                lines[row].push(val.toFixed(3));
                return lines;
            }, [])
            .map(row => row.join(", "))
            .join("\n");

        appendCliLine("sender-cli", `> Noise field generated locally (WASM):`);
        appendCliLog("sender-cli", senderNoiseText);

        // 2. Token an Backend senden
        fetch("/set-token", {
            method: "POST",
            body: new FormData(tokenForm)
        })
        .then(res => res.json())
        .then(data => {
            const receiverCLI = document.getElementById("receiver-cli");

            data.receiver_log.forEach(item => {
                if (item.type === "line") {
                    appendCliLine("receiver-cli", item.text);
                } else if (item.type === "log") {
                    appendCliLog("receiver-cli", item.text);
                }
            });

            tokenInput.disabled = true;
            tokenBtn.disabled = true;
            msgInput.disabled = false;
            msgBtn.disabled = false;
        });
    });

    messageForm.addEventListener("submit", function (e) {
        e.preventDefault();
        fetch("/set-token", {
            method: "POST",
            body: new FormData(tokenForm)
        }).then(() => {
            console.log("Message sent");
        });
    });

}

function appendCliLine(containerId, text) {
    const container = document.getElementById(containerId);
    const div = document.createElement("div");
    div.className = "cli-line";
    div.textContent = text;
    container.appendChild(div);
}

function appendCliLog(containerId, text) {
    const container = document.getElementById(containerId);
    const div = document.createElement("div");
    div.className = "cli-log";
    div.textContent = text;
    container.appendChild(div);
}