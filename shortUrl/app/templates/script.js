 document.getElementById('shorten-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            const originalUrl = document.getElementById('original-url').value;
            const response = await fetch('/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ original_url: originalUrl }),
            });
            const result = await response.json();
            document.getElementById('shortened-url').innerText = `Short URL: ${window.location.origin}/${result.short_url}`;
        });