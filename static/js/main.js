document.querySelector('form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;

    const codeContainer = document.querySelector('.code-container');
    codeContainer.innerHTML = ""; // Vorherige Ausgabe löschen

    try {
        const response = await fetch('/encrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.log && Array.isArray(data.log)) {
            const pre = document.createElement('pre');
            pre.classList.add('cli-log');

            let lines = data.log.map(line => `> ${line}`).join('\n');
            lines += `\n\n[Encrypted Result]\n${data.encrypted}`;
            pre.textContent = lines;

            codeContainer.appendChild(pre);
        } else if (data.formatted) {
            const pre = document.createElement('pre');
            pre.classList.add('cli-log');
            pre.textContent = data.formatted;
            codeContainer.appendChild(pre);
        } else {
            codeContainer.textContent = "Fehler: Keine gültige Log-Ausgabe erhalten.";
        }
    } catch (err) {
        codeContainer.textContent = `Fehler beim Senden der Anfrage: ${err.message}`;
    }
});
