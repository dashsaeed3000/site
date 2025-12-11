// for menu scroll
const pageLink = document.querySelectorAll(".main-sidebar .nav-link");

pageLink.forEach((elem) => {
elem.addEventListener("click", (e) => {
    e.preventDefault();
    
    let WinUrl = window.location.pathname.split('/');
    if(WinUrl[WinUrl.length - 1] == 'index.html'){
        window.location.assign(elem.getAttribute("href"))
    }
    
    let headerOffset = 80;
    let elemOffsetTop = document.querySelector(elem.getAttribute("href"))
    let elementPosition = elemOffsetTop.getBoundingClientRect().top - headerOffset;
    window.scrollBy(0, elementPosition); 

    });
});