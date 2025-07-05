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

let clientNoiseField = null;
let token = null;
let tokenInput = document.getElementById("token-input");

function setupHandlers() {
    const cipherForm = document.getElementById("cipher-form");
    const tokenForm = document.getElementById("token-form");
    const messageForm = document.getElementById("message-form");

    const tokenBtn = document.getElementById("set-token-btn");

    const msgInput = document.getElementById("message-input");
    const msgBtn = document.getElementById("send-msg-btn");

    cipherForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const senderCLI = document.getElementById("conversation");
        senderCLI.innerHTML = "";

        await appendCliLine("client","> Sending cipher config to host...");

        fetch("/set-cipher", {
            method: "POST",
            body: new FormData(cipherForm)
        })
        .then((response) => response.json())
        .then(async (data) => {

            for (const line of data.receiver_log) {
                await appendCliLine("server", line);
            }

            // Enable next step
            tokenInput.disabled = false;
            tokenBtn.disabled = false;
        });
    });

    tokenForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        await appendCliLine("client", `> Token specified...`);

        token = tokenInput.value;

        await appendCliLine("client", `> Noise field generated locally:`);
        // 1. WASM-generiertes Noise Field im Sender-Terminal anzeigen
        const wasmNoise = window.WasmModule.generate_noise_field(token, 100, 0.1);

        clientNoiseField = Array.from(wasmNoise).map(row =>
            Array.from(row).map(Number)
        );

        // Konvertiere jedes Element zu Number
        const noiseNumbers = Array.from(wasmNoise).map(row =>
            Array.from(row).map(Number)
        );

        const firstRow = noiseNumbers[0];
        const senderNoiseText = "> First row: \n [" + firstRow.map(val => val.toFixed(8)).join(", ") + "]";

        hashFirstRow(firstRow).then(async clientHash  => {
            await appendCliLog("client", senderNoiseText);
            await appendCliLine("client", `> Noise row hash (client): ${clientHash}`);

            // Dann Server-Request starten
            fetch("/set-token", {
                method: "POST",
                body: new FormData(tokenForm)
            })
            .then(res => res.json())
            .then(async data => {
                for (const item of data.receiver_log) {
                    if (item.type === "line") {
                        await appendCliLine("server", item.text);
                    } else if (item.type === "log") {
                        await appendCliLog("server", item.text);
                    }
                }

                // Vergleich Hashes
                const serverHash = data.noise_hash;
                await appendCliLine("client", `> Noise row hash received from server: ${serverHash}`);

                if (clientHash === serverHash) {
                    await appendCliLine("client", "> VALIDATION: Noise rows are IDENTICAL.");
                    await appendCliLine("client", "> Memory Setup complete");

                } else {
                    await appendCliLine("client", "> Noise row mismatch!");
                }

                tokenInput.disabled = true;
                tokenBtn.disabled = true;
                msgInput.disabled = false;
                msgBtn.disabled = false;
            });
        });
    });

    messageForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const message = msgInput.value;
        const coord = [5, 7];
        const token = tokenInput.value;

        // Debug: Check if clientNoiseField is available
        if (!clientNoiseField) {
            await appendCliLine("client", `> ERROR: Noise field not initialized! Please set token first.`);
            return;
        }

        await appendCliLine("client", `> Encrypting message locally with Lorenz cipher...`);
        await appendCliLog("client", `> Plaintext: "${message}"`);
        await appendCliLog("client", `> Coordinates: [${coord.join(", ")}]`);
        await appendCliLog("client", `> Noise field dimensions: ${clientNoiseField.length}x${clientNoiseField[0].length}`);

        const encrypted = await lorenzEncrypt(message, coord, clientNoiseField);

        await appendCliLine("client", `> Encrypted message: "${encrypted}"`);
        await appendCliLine("client", `> Transferring encrypted message to server...`);

        const form = new FormData();
        form.append("enc_message", encrypted);
        form.append("coords", coord.join(","));

        fetch("/message", {
            method: "POST",
            body: form
        })
        .then(res => res.json())
        .then(async data => {
            for (const item of data.receiver_log) {
                if (item.type === "line") {
                    await appendCliLine("server", item.text);
                } else if (item.type === "log") {
                    await appendCliLog("server", item.text);
                }
            }

            await appendCliLine("client", `> Decrypted message received: "${data.decrypted_message}"`);
            await appendCliLine("client", `> Rotating token... `);

            const newToken = await rotateToken(encrypted);

            await appendCliLine("client", `> Server rotated token to: "${data.new_token}"`);
            await appendCliLine("client", `> Local rotated token: "${newToken}"`);

            if (newToken === data.new_token) {
                await appendCliLine("client", "> Token SYNC confirmed");
            } else {
                await appendCliLine("client", "> Token mismatch! Desync occurred");
            }

        });
    });
}

async function appendCliLine(senderType, text) {
    const container = document.getElementById("conversation");

    const convItem = document.createElement("div");
    convItem.className = `conv-item ${senderType}`;

    const cliLine = document.createElement("div");
    cliLine.className = `cli-line ${senderType === "client" ? "cli-left" : "cli-right"}`;
    cliLine.textContent = text;

    convItem.appendChild(cliLine);
    container.appendChild(convItem);
    container.scrollTop = container.scrollHeight;

    // 300ms delay nach jedem appendCliLine
    await new Promise(resolve => setTimeout(resolve, 300));
}

async function appendCliLog(senderType, text) {
    const container = document.getElementById("conversation");

    const convItem = document.createElement("div");
    convItem.className = `conv-item ${senderType}`;

    const cliLine = document.createElement("div");
    cliLine.className = `cli-log ${senderType === "client" ? "cli-left" : "cli-right"}`;
    cliLine.textContent = text;

    convItem.appendChild(cliLine);
    container.appendChild(convItem);
    container.scrollTop = container.scrollHeight;

    // 300ms delay nach jedem appendCliLog
    await new Promise(resolve => setTimeout(resolve, 300));
}


function hashFirstRow(row) {
    const buffer = new Float64Array(row).buffer;
    return crypto.subtle.digest("SHA-256", buffer).then(hashBuffer => {
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    });
}

async function lorenzEncrypt(plaintext, coord, noiseField) {
    const sigma = 10;
    const rho = 28;
    const beta = 8 / 3;
    const dt = 0.01;
    const stepsPerChar = 100;

    const [cx, cy] = coord;
    let x = noiseField[cx][cy];
    let y = noiseField[(cx + 1) % noiseField.length][cy];
    let z = noiseField[cx][(cy + 1) % noiseField[0].length];

    let encrypted = "";
    const keyStream = [];

    for (let i = 0; i < plaintext.length; i++) {
        for (let j = 0; j < stepsPerChar; j++) {
            const dx = sigma * (y - x);
            const dy = x * (rho - z) - y;
            const dz = x * y - beta * z;

            x += dx * dt;
            y += dy * dt;
            z += dz * dt;

        }

        const byte = Math.floor(Math.abs(z * 1e6)) % 256;
        keyStream.push(byte);

        const charCode = plaintext.charCodeAt(i);
        encrypted += String.fromCharCode(charCode ^ byte);
    }

    const formattedKeyStream = keyStream
    .map(n => n.toString().padStart(3, " "))
    .reduce((acc, val, idx) => {
        const sep = (idx + 1) % 10 === 0 ? "\n" : " ";
        return acc + val + sep;
    }, "");

    await appendCliLog("client", `> Client keystream bytes:\n${formattedKeyStream}`);

    return encrypted;
}

function lorenzDecrypt(ciphertext, coord, noiseField) {
    return lorenzEncrypt(ciphertext, coord, noiseField);
}

async function hashMessage(msg) {
    const data = new TextEncoder().encode(msg);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, "0")).join("");
}

async function rotateToken(encrypted) {
    const hash = await hashMessage(encrypted);
    const newToken = window.WasmModule.rotate_token(token, hash);
    const wasmNoise = window.WasmModule.generate_noise_field(newToken, 100, 0.1);

    clientNoiseField = Array.from(wasmNoise).map(row =>
        Array.from(row).map(Number)
    );

    // Globales Token updaten
    token = newToken;
    tokenInput.value = newToken;

    return newToken;
}