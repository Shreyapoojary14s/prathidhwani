$(document).ready(function(){
    // Function to load JSON data from a given API endpoint and render it into #main-content
    function loadContent(apiUrl) {
        // Show a loading spinner
        $("#main-content").html(`
          <div class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="sr-only">Loading...</span>
            </div>
          </div>
        `);
        $.getJSON(apiUrl, function(data){
            let html = `<div class="text-center">`;
            html += `<h1 class="display-4" style="color: #6a1b9a;">${data.title || ''}</h1>`;
            html += `<p class="lead" style="color: #4a148c;">${data.description || ''}</p>`;
            if(data.current_time){
                html += `<p><strong>Time:</strong> ${data.current_time}</p>`;
            }
            if(data.raga_name && data.raga_name !== "Unknown"){
                html += `<p><strong>Raga:</strong> ${data.raga_name}</p>`;
            }
            if(data.songs && data.songs.length > 0){
                // Build the embed URL for the first song with autoplay and mute enabled
                const firstSongEmbed = data.songs[0].link.replace("watch?v=", "embed/") + "?autoplay=1&mute=1";
                html += `
                  <div class="embed-responsive embed-responsive-16by9 mb-4">
                    <iframe class="embed-responsive-item" src="${firstSongEmbed}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                  </div>
                `;
                // List remaining songs
                html += `<div class="list-group">`;
                $.each(data.songs, function(index, song){
                    html += `<a href="${song.link}" class="list-group-item list-group-item-action" target="_blank">🎵 ${song.title}</a>`;
                });
                html += `</div>`;
            } else {
                html += `<p>No songs found.</p>`;
            }
            html += `</div>`;
            $("#main-content").html(html);
        }).fail(function(){
            $("#main-content").html(`<div class="alert alert-danger">Error loading content.</div>`);
        });
    }
    
    // Home screen content
    function loadHome(){
        $("#main-content").html(`
          <div class="jumbotron text-center" style="background-color: #fafafa;">
            <h1 class="display-4" style="color: #6a1b9a;">Welcome to Prathidwani SPA</h1>
            <p class="lead" style="color: #4a148c;">Experience the divine world of Carnatic music with curated ragas.</p>
            <a href="#" class="btn btn-lg btn-primary" id="btn-discover">Let's Dive In</a>
          </div>
        `);
    }
    
    loadHome(); // Load the home screen on page load

    // Navigation: Home
    $("#nav-home-link, #nav-home").click(function(e){
        e.preventDefault();
        loadHome();
    });

    // Navigation: Discover (shows exploration options)
    $("#nav-discover-link, #btn-discover").click(function(e){
        e.preventDefault();
        let html = `
          <div class="text-center mt-5">
            <h1 class="display-4" style="color: #6a1b9a;">Discover the Magic of Carnatic Music</h1>
            <p class="lead" style="color: #4a148c;">Choose your exploration path:</p>
            <div class="btn-group mt-4" role="group">
              <button class="btn btn-lg shadow px-4 py-2" style="background-color: #ff6f00; color: #fff; border-radius: 10px;" id="btn-time">Time</button>
              <button class="btn btn-lg shadow px-4 py-2" style="background-color: #d50000; color: #fff; border-radius: 10px;" id="btn-emotion">Emotion</button>
              <button class="btn btn-lg shadow px-4 py-2" style="background-color: #2e7d32; color: #fff; border-radius: 10px;" id="btn-season">Season</button>
              <button class="btn btn-lg shadow px-4 py-2" style="background-color: #1976d2; color: #fff; border-radius: 10px;" id="btn-enthusiastic">Enthusiastic Listener</button>
            </div>
          </div>
        `;
        $("#main-content").html(html);
    });

    // Navigation: About
    $("#nav-about-link").click(function(e){
        e.preventDefault();
        $.getJSON("/api/about", function(data){
            let html = `
              <div class="text-center mt-5">
                <h1 class="display-4" style="color: #6a1b9a;">${data.title}</h1>
                <p class="lead" style="color: #4a148c;">${data.description}</p>
              </div>
            `;
            $("#main-content").html(html);
        }).fail(function(){
            $("#main-content").html('<div class="alert alert-danger">Error loading About info.</div>');
        });
    });

    // Button Handlers for each mode
    $(document).on("click", "#btn-time", function(){
        loadContent("/api/time");
    });
    $(document).on("click", "#btn-emotion", function(){
        loadContent("/api/emotion");
    });
    $(document).on("click", "#btn-season", function(){
        loadContent("/api/season");
    });
    $(document).on("click", "#btn-enthusiastic", function(){
        loadContent("/api/enthusiastic");
    });
});
