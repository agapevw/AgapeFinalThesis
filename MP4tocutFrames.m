%function MP4toCutFrames(filename,startframe,endframe)

% Takes MP4 video and produces frames in a named folder of all frames between and
% including provided start and end frames.
% 
% INPUT
% filename: the name of your video without .MP4
% startframe: the first frame of the range of desired extracted frames
% endframe: the last frame of the desired extracted frames
% OUTPUT
% folder containing pngs of cut frames  
% Written by: Jeffrey Hainer [June 09, 2023]

function MP4tocutFrames(filename,startframe,endframe)

%Load in video
%videoObject = chkVideoReader(sprintf('%s.MP4',filename));
videoObject =VideoReader(filename)


%Add frame numbers into video name as string then create folder with string
%name in current directory
str = append(filename(1:end-4),'_',string(startframe),'-',string(endframe));%Add frame numbersinto video name as string
mkdir(str);

%Designate created folder as output folder for frames
outputFolder=(str);

%Make an array of desired frame numbers to extract based on start and
%endframes
%pickedframes = [startframe endframe];
pickedframessize = (startframe:endframe);

%Extract frames and save them in created folder.
for frame=1:length(pickedframessize);
vid1Frames=read(videoObject,startframe+(frame-1));
outputBaseFileName=sprintf('%3.3d.png',frame);
outputFullFileName=fullfile(outputFolder,outputBaseFileName);
imwrite(vid1Frames(:,:,:,1),outputFullFileName,'png');
end
