local dfpwm = require("cc.audio.dfpwm")

local speaker = peripheral.find("speaker")
local monitor = peripheral.find("monitor")

local videoFile = "/video.nfv"
local audioFile = "/audio.dfpwm"

local videoData = {}
for line in io.lines(videoFile) do
    table.insert(videoData, line)
end

local resolution = { videoData[1]:match("(%d+) (%d+)") }
local fps = tonumber(videoData[1]:match("%d+ %d+ (%d+)"))
table.remove(videoData, 1)

local frameIndex = 2
function nextFrame()
    local frame = {}
    for i = 1, resolution[2] do
        if frameIndex + i > #videoData then
            break
        end
        table.insert(frame, videoData[frameIndex + i])
    end
    frame = paintutils.parseImage(table.concat(frame, "\n"))
    frameIndex = frameIndex + resolution[2]
    if frameIndex > #videoData then
        return false
    end

    paintutils.drawImage(frame, 1, 1)
    os.sleep(1 / fps)
    return true
end

monitor.setTextScale(1)
term.redirect(monitor)

function audioLoop()
    local decoder = dfpwm.make_decoder()
    for chunk in io.lines(audioFile, 16 * 1024) do
        local buffer = decoder(chunk)
        while not speaker.playAudio(buffer, 3) do
            os.pullEvent("speaker_audio_empty")
        end
    end
end

function videoLoop()
    while nextFrame() do end
end

parallel.waitForAll(audioLoop, videoLoop)

term.clear()
term.redirect(term.native())
