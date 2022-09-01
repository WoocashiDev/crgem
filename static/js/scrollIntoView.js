const intro = document.querySelector('#intro');
const workflow = document.getElementById('workflow')
const contact = document.getElementById('contact')
const introLink = document.querySelector('#intro-link');
const workflowLink = document.getElementById('workflow-link')
const contactLink = document.getElementById('contact-link')

let elements = [
    {
    "section": intro,
    "trigger": introLink,
    },
    {
    "section": workflow,
    "trigger": workflowLink,
    },
    {
    "section": contact,
    "trigger": contactLink,
    },

]

elements.forEach((element) => {

let section = element.section
let trigger = element.trigger

trigger.addEventListener('click', (event)=>{
    event.preventDefault()
    section.scrollIntoView({behavior: 'smooth', block: 'center'});
    trigger.classList.add('active');
})

section.addEventListener('mouseenter', (event)=>{
    trigger.classList.add('active');
})

section.addEventListener('mouseleave', (event)=>{
    trigger.classList.remove('active');
})

})