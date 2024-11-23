var mediaQuery = window.matchMedia('(max-width: 46.1875em)');
if (mediaQuery.matches) {
    var contents = document.getElementsByClassName("post-content");
    for (var i = 0; i < contents.length; i++) {
        var content = contents[i].innerHTML;
        if (content.length > 40) {
            content = content.substring(0, 32) + "...";
            contents[i].innerHTML = content;
        }
    }

    var noti_icon = document.querySelector(".nav_noti")
    var nav_edit =document.querySelector(".nav_edit")
    var nav_search = document.querySelector(".nav_search")

    var blog_page = document.querySelector(".blog-page")
    var home_page = document.querySelector(".home-page")
    var noti_page = document.querySelector(".notification")
    var search_page = document.querySelector(".blog-user-info")

    nav_search.addEventListener("click", function(){
      search_page.classList.remove("none");
      var computedStyle = window.getComputedStyle(search_page);
      var zIndex = parseInt(computedStyle.getPropertyValue('z-index'));
    
      if(zIndex === -10){
        search_page.style.zIndex = '10'; // Mở cửa sổ tìm kiếm
      } else {
        search_page.style.zIndex = '-10'; // Đóng cửa sổ tìm kiếm
      }
    });
    noti_icon.addEventListener("click", function() {
      noti_page.classList.remove("none");
      var isClosed = noti_page.style.display !== 'flex';
      if (isClosed){
        noti_page.style.display = 'flex';
      }
    })

    nav_edit.addEventListener("click", function() {
        if(home_page.classList.contains("none")) {
            home_page.classList.remove("none")
        }
        var isClosed = blog_page.style.display !== 'flex';
        if (isClosed){
          blog_page.style.display = 'flex';
        }
    })
    var navbar = document.getElementById('mobile-navbar');
    var moblieMenu = document.getElementById('mobile-menu');
    moblieMenu.onclick = function(){
      var isClosed = navbar.style.overflow === 'hidden';
      if (isClosed){
        navbar.style.overflow = 'initial';
      } else{
        navbar.style.overflow = 'hidden';
      }
    }
    function toConservation() {
      var conservation = document.getElementById('conservation');
      var inboxList = document.getElementById('inbox-list')
      var isOpened = inboxList.style.display !== 'none';
      console.log("isOpened");
        if (isOpened){
          conservation.style.display = 'block';
          inboxList.style.display = "none";
        }
      }
      function BacktoInboxPeo() {
        var conservation = document.getElementById('conservation');
        var inboxList = document.getElementById('inbox-list')
        var isOpened = conservation.style.display !== 'none';
          if (isOpened){
            conservation.style.display = 'none';
            inboxList.style.display = "block";
          }
      }
      function closeSearch() {
        console.log("1");
        var search = document.getElementById('mobile-search');
        var isOpened = search.style.display !== 'none';
        if (isOpened){
          search.style.display = 'none';
        }
      }
}