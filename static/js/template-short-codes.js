window.addEventListener('DOMContentLoaded', event => {

    const buttons = document.querySelectorAll("button.short-code-button");
    console.log(buttons);


    buttons.forEach(button => {
        button.addEventListener('click', event => {
        console.log(event.target.dataset.shortcode)
            let iframe = document.querySelector('#cke_1_contents > iframe')
            last_paragraph = iframe.contentWindow.document.body.querySelector('p:last-of-type')
            let shortcode = document.createTextNode(event.target.dataset.shortcode)
            console.log(last_paragraph)
            console.log(iframe)
            console.log(shortcode)
            last_paragraph.appendChild(shortcode)
        })
    });
});