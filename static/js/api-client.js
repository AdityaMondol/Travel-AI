class APIClient {
    constructor(baseURL = window.location.origin) {
        this.baseURL = baseURL;
        this.timeout = 60000;
        this.retries = 3;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: this.timeout
        };

        const config = { ...defaultOptions, ...options };

        for (let attempt = 0; attempt < this.retries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), config.timeout);

                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    if (response.status === 429) {
                        await this.delay(1000 * (attempt + 1));
                        continue;
                    }
                    throw new Error(`HTTP ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                if (attempt === this.retries - 1) {
                    console.error(`API Error [${endpoint}]:`, error);
                    throw error;
                }
                await this.delay(1000 * (attempt + 1));
            }
        }
    }

    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    stream(endpoint, onMessage, onError) {
        const url = `${this.baseURL}${endpoint}`;
        const eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (e) {
                console.error('Stream parse error:', e);
            }
        };

        eventSource.onerror = (error) => {
            console.error('Stream error:', error);
            eventSource.close();
            if (onError) onError(error);
        };

        return eventSource;
    }

    async downloadFile(endpoint, filename, format = 'html') {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}?format=${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ destination: filename })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${filename}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }
}

const apiClient = new APIClient();
