var mediaQuery = window.matchMedia(
  "(min-width: 46.25em) and (max-width: 63.9375em)"
);
if (mediaQuery.matches) {
  var contents = document.getElementsByClassName("post-content");
  for (var i = 0; i < contents.length; i++) {
    var content = contents[i].innerHTML;
    if (content.length > 48) {
      content = content.substring(0, 59) + "...";
      contents[i].innerHTML = content;
    }
  }

  var itemContents = document.getElementsByClassName("item-content");
  for (var i = 0; i < itemContents.length; i++) {
    var itemContent = itemContents[i].innerHTML;
    var lineItemContent = itemContent.split("\n");
    for (var j = 0; j < lineItemContent.length; j++) {
      if (lineItemContent[j].trim().length > 0) {
        console.log(lineItemContent[j]);
        if (lineItemContent[j].length > 70) {
          lineItemContent[j] = lineItemContent[j].substring(0, 60) + "...";
          itemContents[i].innerHTML = lineItemContent[j];
        } else {
          itemContents[i].innerHTML = lineItemContent[j] + "...";
        }
        break;
      }
    }
  }

  var noti_icon = document.querySelector(".nav_noti");
  var nav_edit = document.querySelector(".nav_edit");

  var blog_page = document.querySelector(".blog-page");
  var home_page = document.querySelector(".home-page");
  var blog_noti = document.querySelector(".blog-noti");

  var blogSearch = document.querySelector(".blog-user-info");
  var btnSearch = document.querySelector(".btn-search");
  var info = document.querySelector(".right-side-2");

  if (!blog_page.classList.contains("none")) {
    blog_page.classList.add("none");
  }

  if (!blog_noti.classList.contains("none")) {
    blog_noti.classList.add("none");
  }

  if (!document.querySelector(".notification").classList.contains("none")) {
    document.querySelector(".notification").classList.add("none");
  }

  if (!document.querySelector(".blog-user-info").classList.contains("none")) {
    document.querySelector(".blog-user-info").classList.add("none");
  }

  // Search
  var search = document.querySelector(".right-side1");
  var overlay = document.createElement("div");
  overlay.classList.add("overlay", "none");
  document.body.appendChild(overlay);
  btnSearch.addEventListener("click", function () {
    if (blog_noti.classList.contains("none")) {
      blog_noti.classList.remove("none");
      if (search.classList.contains("none")) {
        search.classList.remove("none");
      }
      if (!info.classList.contains("none")) {
        info.classList.add("none");
      }
      if (overlay.classList.contains("none")) {
        overlay.classList.remove("none");
      }
      if (blogSearch.classList.contains("none")) {
        blogSearch.classList.remove("none");
      }
      if (!blog_page.classList.contains("none")) {
        blog_page.classList.add("none");
      }
      if (!document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.add("none");
      }
      if (home_page.classList.contains("none")) {
        home_page.classList.remove("none");
      }
    } else {
      if (search.classList.contains("none")) {
        search.classList.remove("none");
      }
      if (!info.classList.contains("none")) {
        info.classList.add("none");
      }
      if (overlay.classList.contains("none")) {
        overlay.classList.remove("none");
      }
      if (!document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.add("none");
      }
      if (blogSearch.classList.contains("none")) {
        blogSearch.classList.remove("none");
      }
      if (home_page.classList.contains("none")) {
        home_page.classList.remove("none");
      }
    }

    overlay.addEventListener("click", function () {
      search.classList.add("none");
      overlay.classList.add("none");
    });
  });

  // Post blog
  nav_edit.addEventListener("click", function () {
    if (blog_page.classList.contains("none")) {
      blog_page.classList.remove("none");
      if (!blog_noti.classList.contains("none")) {
        blog_noti.classList.add("none");
      }
      if (!home_page.classList.contains("none")) {
        home_page.classList.add("none");
      }
      if (!document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.add("none");
      }
      if (
        !document.querySelector(".blog-user-info").classList.contains("none")
      ) {
        document.querySelector(".blog-user-info").classList.add("none");
      }
    } else {
      if (!blog_noti.classList.contains("none")) {
        blog_noti.classList.add("none");
      }
      if (!home_page.classList.contains("none")) {
        home_page.classList.add("none");
      }
      if (!document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.add("none");
      }
      if (
        !document.querySelector(".blog-user-info").classList.contains("none")
      ) {
        document.querySelector(".blog-user-info").classList.add("none");
      }
    }
  });

  // Notification
  noti_icon.addEventListener("click", function () {
    if (blog_noti.classList.contains("none")) {
      blog_noti.classList.remove("none");
      if (!blog_page.classList.contains("none")) {
        blog_page.classList.add("none");
      }
      if (!home_page.classList.contains("none")) {
        home_page.classList.add("none");
      }
      if (document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.remove("none");
      }
      if (
        !document.querySelector(".blog-user-info").classList.contains("none")
      ) {
        document.querySelector(".blog-user-info").classList.add("none");
      }
    } else {
      if (document.querySelector(".notification").classList.contains("none")) {
        document.querySelector(".notification").classList.remove("none");
      }
      if (
        !document.querySelector(".blog-user-info").classList.contains("none")
      ) {
        document.querySelector(".blog-user-info").classList.add("none");
      }
      if (!home_page.classList.contains("none")) {
        home_page.classList.add("none");
      }
    }
  });

  // Chat box
  var newChat = document.querySelector("#new_chat_btn");
  var chatBody = document.querySelector(".chatbox-bg");
  console.log(chatBody);
  // chatBody.appendChild(overlay);
  newChat.addEventListener("click", function () {
    overlay.classList.remove("none");
  });
}