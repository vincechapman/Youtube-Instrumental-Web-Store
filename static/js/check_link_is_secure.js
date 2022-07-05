var current_url = window.location.href

if (current_url.startsWith("http://127.0.0.1") || current_url.startsWith("http://localhost")) {
    console.log('Running on a local server.')
} else {
    if (current_url.startsWith("http://")) {
        let new_url = current_url.replace("http://", "https://")
        window.location.replace(new_url);
    }
}