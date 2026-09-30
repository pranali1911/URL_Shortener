
function getCookie(name) {

    let cookieValue = null;

    if (document.cookie) {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}


async function loadUrls() {

    const response = await fetch("/api/urls");

    if (!response.ok) {

        document.getElementById("urlList").innerText =
            "Please login first.";

        return;
    }

    const data = await response.json();

    const urls = data.results || data;

    document.getElementById("urlCount").innerText =
        urls.length + (urls.length === 1 ? " Link" : " Links");


    let html = "";


    urls.forEach(function(url) {

        const shortUrl =
            window.location.origin + "/" + url.short_code;


        html += `
            <div class="url-item">

                <div class="original-url">
                    ${url.original_url}
                </div>

                <div class="short-url">

                    <a href="/${url.short_code}" target="_blank">
                        ${shortUrl}
                    </a>

                    <button
                        class="copy-button"
                        onclick="copyUrl('${shortUrl}')"
                    >
                        Copy
                    </button>

                </div>

            </div>
        `;
    });


    if (html === "") {

        html = `
            <div class="loading">
                No URLs created yet.
            </div>
        `;
    }


    document.getElementById("urlList").innerHTML = html;
}


async function copyUrl(url) {

    await navigator.clipboard.writeText(url);

    alert("Short URL copied!");
}


document.getElementById("urlForm").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const originalUrl =
            document.getElementById("original_url").value;

        const customAlias =
            document.getElementById("custom_alias").value;

        const expiresAt =
            document.getElementById("expires_at").value;


        const data = {
            original_url: originalUrl
        };


        if (customAlias) {
            data.custom_alias = customAlias;
        }


        if (expiresAt) {

            data.expires_at =
                new Date(expiresAt).toISOString();
        }


        const response = await fetch("/api/urls", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },

            body: JSON.stringify(data)

        });


        const result = await response.json();


        if (response.ok) {

            document.getElementById("message").innerText =
                "URL created successfully.";

            document.getElementById("urlForm").reset();

            loadUrls();

        } else {

            document.getElementById("message").innerText =
                JSON.stringify(result);
        }

    }
);


loadUrls();

