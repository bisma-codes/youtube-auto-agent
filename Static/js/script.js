let selectedTitle = "";
let finalIdea = "";
let scriptText = "";
let audioFilename = ""; // This will now store paths like "assets/audio_local/voiceover_....mp3"
let lastGeneratedVideoPath = ""; // NEW: To store the path of the last generated video

function setStageActive(stageId) {
    document.querySelectorAll(".stage").forEach(el => el.classList.remove("active"));
    const el = document.getElementById(stageId);
    if (el) el.classList.add("active");

    document.querySelectorAll(".step").forEach(step => step.style.display = "none");

    switch (stageId) {
        case "stage-idea":
            document.querySelector(".step-idea").style.display = "block";
            break;
        case "stage-variation":
            document.querySelector(".step-variation").style.display = "block";
            break;
        case "stage-script":
            document.querySelector(".step-script").style.display = "block";
            break;
        case "stage-audio":
            document.querySelector(".step-audio").style.display = "block";
            break;
        case "stage-video":
            document.querySelector(".step-video").style.display = "block";
            break;
        case "stage-seo":
            document.querySelector(".step-seo").style.display = "block";
            break;
        case "stage-upload":
            document.querySelector(".step-upload").style.display = "block";
            break;
    }
}

async function generateTrendingTitles() {
    const topic = document.getElementById("topicInput").value.trim();
    if (!topic) return alert("Please enter a topic!");
    setStageActive("stage-idea");

    // Add loader
    const loader = document.getElementById("loader");
    loader.textContent = "🧠 Generating trending titles...";
    loader.style.display = "block";

    const res = await fetch("/generate_titles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
    });

    loader.style.display = "none"; // Hide loader

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to get trending titles: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    const list = document.getElementById("trendingTitles");
    list.innerHTML = "";

    if (data.titles && data.titles.length > 0) {
        data.titles.forEach(title => {
            const li = document.createElement("li");
            li.textContent = title;
            li.onclick = () => {
                selectedTitle = title;
                generateIdeaVariations();
            };
            list.appendChild(li);
        });
        setStageActive("stage-variation");
    } else {
        alert("No idea variations found for this title."); // This alert was previously "No trending titles found..."
    }
}

async function generateIdeaVariations() {
    if (!selectedTitle) return;
    setStageActive("stage-variation");

    // Add loader
    const loader = document.getElementById("loader");
    loader.textContent = "💡 Generating idea variations...";
    loader.style.display = "block";

    const res = await fetch("/generate_variations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected_title: selectedTitle })
    });

    loader.style.display = "none"; // Hide loader

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to get idea variations: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    const list = document.getElementById("variationIdeas");
    list.innerHTML = "";

    if (data.variations && data.variations.length > 0) {
        data.variations.forEach(idea => {
            const li = document.createElement("li");
            li.textContent = idea;
            li.onclick = () => {
                finalIdea = idea;
                generateScript();
            };
            list.appendChild(li);
        });
        setStageActive("stage-script");
    } else {
        alert("No idea variations found for this title.");
    }
}

async function generateScript() {
    if (!finalIdea) return alert("Please select an idea first.");
    setStageActive("stage-script");

    // Add loader
    const loader = document.getElementById("loader");
    loader.textContent = "✍️ Generating script...";
    loader.style.display = "block";

    const res = await fetch("/generate_script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea: finalIdea })
    });

    loader.style.display = "none"; // Hide loader

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to generate script: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    scriptText = data.script;
    document.getElementById("scriptPreview").value = scriptText;
    setStageActive("stage-audio");
}

async function generateAudio() {
    const voiceSelector = document.getElementById("voiceSelector");
    const voiceId = voiceSelector.value;

    if (!scriptText) return alert("No script text available.");

    setStageActive("stage-audio");

    // Add loader
    const loader = document.getElementById("loader");
    loader.textContent = "🎤 Generating audio...";
    loader.style.display = "block";

    const res = await fetch("/generate_audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: scriptText, voice_id: voiceId })
    });

    loader.style.display = "none"; // Hide loader

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to generate audio: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    if (data.audio_path) {
        audioFilename = data.audio_path;
        const audioPlayer = document.getElementById("audioPlayer");
        audioPlayer.src = `/download_audio/${audioFilename}`; 
        audioPlayer.style.display = "block";
        audioPlayer.load(); // Load the new source
        audioPlayer.play();
        setStageActive("stage-video");
    } else {
        alert("Audio generation failed: No audio path returned.");
    }
}

async function generateVideo() {
    setStageActive("stage-video");

    const loader = document.getElementById("loader");
    const videoPlayer = document.getElementById("videoPlayer");
    const downloadLink = document.getElementById("downloadLink");

    loader.textContent = "🎥 Generating video...";
    loader.style.display = "block";
    videoPlayer.style.display = "none";
    downloadLink.style.display = "none";

    const res = await fetch("/generate_video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            script: scriptText,
            audio_path: audioFilename
        })
    });

    loader.style.display = "none";

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to generate video: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    const videoPath = data.video_path;

    if (videoPath) {
        lastGeneratedVideoPath = videoPath; // NEW: Store the video path globally

        videoPlayer.src = `/Static/videos/${videoPath.split('/').pop()}`;
        videoPlayer.style.display = "block";
        videoPlayer.load();
        videoPlayer.play();

        downloadLink.href = `/Static/videos/${videoPath.split('/').pop()}`;
        downloadLink.download = videoPath.split('/').pop();
        downloadLink.style.display = "block";
        
        setStageActive("stage-seo");
    } else {
        alert("Video generation failed: No video path returned.");
    }
}

async function optimizeSEO() {
    if (!scriptText) return alert("No script text available for SEO optimization.");
    setStageActive("stage-seo");

    const loader = document.getElementById("loader");
    loader.textContent = "🔍 Optimizing SEO...";
    loader.style.display = "block";

    const res = await fetch("/optimize_seo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script: scriptText })
    });

    loader.style.display = "none";

    if (!res.ok) {
        const errorData = await res.json();
        return alert(`Failed to optimize SEO: ${errorData.error || res.statusText}`);
    }

    const data = await res.json();
    // Assuming data contains title, description, tags
    const title = data.title || 'N/A';
    const description = data.description || 'N/A';
    const tags = data.tags ? data.tags.join(", ") : 'N/A';
    
    const output = `Title: ${title}\nDescription: ${description}\nTags: ${tags}`;
    document.getElementById("seoOutput").value = output;
    setStageActive("stage-upload");
}

async function uploadVideo() {
    if (!lastGeneratedVideoPath) {
        return alert("No video has been generated yet for upload.");
    }

    // NEW: Extract SEO metadata from the textarea
    const seoOutputText = document.getElementById("seoOutput").value;
    const seoLines = seoOutputText.split('\n');
    const titleLine = seoLines.find(line => line.startsWith('Title:'));
    const descriptionLine = seoLines.find(line => line.startsWith('Description:'));
    const tagsLine = seoLines.find(line => line.startsWith('Tags:'));

    // Default values if not found or N/A
    const title = titleLine && titleLine.includes('N/A') ? "AI Generated Video" : (titleLine ? titleLine.substring('Title:'.length).trim() : "AI Generated Video");
    const description = descriptionLine && descriptionLine.includes('N/A') ? "A video generated by AI." : (descriptionLine ? descriptionLine.substring('Description:'.length).trim() : "A video generated by AI.");
    const tags = tagsLine && tagsLine.includes('N/A') ? ["AI", "Generated", "YouTube"] : (tagsLine ? tagsLine.substring('Tags:'.length).trim().split(', ').filter(Boolean) : ["AI", "Generated", "YouTube"]);


    setStageActive("stage-upload");
    
    const loader = document.getElementById("loader");
    loader.textContent = "📤 Uploading video...";
    loader.style.display = "block";

    // NEW: Send video path and SEO data to the backend
    const res = await fetch("/upload_video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            video_path: lastGeneratedVideoPath, // Send the backend-relative path
            title: title,
            description: description,
            tags: tags
        })
    });
    
    loader.style.display = "none";

    const uploadSuccessDiv = document.getElementById("uploadSuccess");
    uploadSuccessDiv.style.display = "none"; // Hide initially in case of re-upload
    uploadSuccessDiv.style.removeProperty("color"); // Reset color

    if (!res.ok) {
        const errorData = await res.json();
        uploadSuccessDiv.innerHTML = `❌ Failed to upload video: ${errorData.error || res.statusText}`;
        uploadSuccessDiv.style.color = "#FF4444"; // Red for error
        uploadSuccessDiv.style.display = "block";
        return; // Stop execution on error
    }

    const data = await res.json();
    if (data.status === "uploaded" && data.video_id) {
        // CORRECTED YOUTUBE LINK FORMAT
        const youtubeLink = `http://www.youtube.com/watch?v=${data.video_id}`;
        uploadSuccessDiv.innerHTML = `✅ Your video has been successfully uploaded! <a href="${youtubeLink}" target="_blank">View on YouTube</a>`;
        uploadSuccessDiv.style.color = "#4CAF50"; // Green for success
        uploadSuccessDiv.style.display = "block";
    } else {
        uploadSuccessDiv.innerHTML = `❌ Video upload failed: ${data.message || "Unknown error."}`;
        uploadSuccessDiv.style.color = "#FF4444";
        uploadSuccessDiv.style.display = "block";
    }
}

async function fetchVoices() {
    const voiceSelector = document.getElementById("voiceSelector");
    voiceSelector.innerHTML = ""; // Clear existing options

    // Add a default local voice option
    const defaultOption = document.createElement("option");
    defaultOption.value = "local_default"; // A dummy ID
    defaultOption.textContent = "System Default (Local)";
    voiceSelector.appendChild(defaultOption);

    try {
        // NOTE: The /get_voices route was commented out/removed from your main.py.
        // This fetch call will likely result in a 404.
        // If you intend to use ElevenLabs voices, you'll need to re-implement
        // the /get_voices route in main.py.
        const res = await fetch("/get_voices"); 
        if (res.ok) {
            const data = await res.json();
            if (data.voices && data.voices.length > 0) {
                voiceSelector.innerHTML = ""; // Clear default if real voices are available
                data.voices.forEach(voice => {
                    const option = document.createElement("option");
                    option.value = voice.voice_id;
                    option.textContent = `${voice.name} (${voice.labels?.accent || 'Default'})`;
                    voiceSelector.appendChild(option);
                });
            } else {
                console.warn("ElevenLabs voices fetched, but list is empty. Keeping local default.");
            }
        } else {
            console.error("Failed to fetch ElevenLabs voices. Using local default. Status:", res.status);
            const errorData = await res.json();
            console.error("ElevenLabs error:", errorData.error);
        }
    } catch (e) {
        console.error("Error fetching voices:", e);
    }
}

window.onload = () => {
    fetchVoices(); 
    setStageActive("stage-idea");
};