%function FramestoAVI(startframe,endframe,foldername,NameValArgs)

% Takes folder containing frames and produces AVI video

% INPUT
% foldername:The name of the folder with frames to be converted into AVI
% startframe: the first frame of the range of extracted frames within folder
% endframe: the last frame of the range of extracted frames within folder
% NAME-VALUE ARGUMENTS
% colour: option to save avi in colour or grayscale. Grayscale is "0",
% colour is any number but "0" (such as "1"). Default is colour.
% OUTPUT
% AVI video

% Written by: Jeffrey Hainer [June 09, 2023]
function FramestoAVI(startframe,endframe,foldername,NameValArgs)

arguments
    startframe (1,1) double
    endframe (1,1) double
    foldername (:,:) string = ""
    NameValArgs.colour (1,1) double = 1
end

% Create the video object.
if NameValArgs.colour(1,1) == 0
    video = VideoWriter(foldername,'Grayscale AVI'); % Create the video object.
else
    video = VideoWriter(foldername,'Uncompressed AVI'); % Create the video object.
end
open(video); % Open the file for writing
N=(endframe-startframe+1); % Where N is the separate number of PNG image files.


for k = 1 : N 
    if NameValArgs.colour(1,1) == 0
        I = rgb2gray(imread(fullfile(foldername, sprintf('%3.3d.png', k))));%% Read the next image, convert to grayscale
    else
        I = imread(fullfile(foldername, sprintf('%3.3d.png', k)));%% Read the next image
    end
    writeVideo(video,I); % Write the image to file.
end
close(video);
