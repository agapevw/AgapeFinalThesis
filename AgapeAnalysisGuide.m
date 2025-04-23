%%%%%%%%%% Agape Analysis Guide %%%%%%%%%%
% This is the master code that runs through the entire process of taking
% output from DLC and turning it into 2D kinematic
% variables. 
%% Step 1- Analyze in DLC
% Once you have the csv and h5 files from DLC, move them into a folder
% called 'DLC Output' with the original AVI file in your 'Working Videos' folder
%% Step 2- Use Mary Python code
% Change line 180 in Mary's code to the path of your videos. Run the code.
%% Step 3- Set Project Details
clear
clc
addpath './Kinematics'%path to this code folder
addpath './Utilities'%path to this code folder
addpath './BaseCode'%path to this code folder
addpath '.'/2025-01-15/ %path to data

filename = "bspot2024_010_T07_SW_5736-6562"; %What is the filename of your video without .avi?
skip=1; %If you digitized every frame skip=1, if you digitized every other frame skip=2
framerate=239.7622;%What is your frame rate?

ans='Step 3 complete!'
%% Step 4- Load in splinex and spliney

splinex=readmatrix(sprintf('%s_x_splined.csv',filename));
spliney=readmatrix(sprintf('%s_y_splined.csv',filename)); 

spliney(1,:)=[]
spliney(:,1)=[]

splinex(1,:)=[]
splinex(:,1)=[]

ans='step 4 complete!'
%% Step 5- Undistort spline
%Load in cameraparams

for i=1:101;
    points(:,1)=splinex(:,i);
    points(:,2)=spliney(:,i);
    [undistortedPoints(:,1:2), reprojectionErrors] = undistortPoints(points, cameraParams);
splinexundist(:,i)=undistortedPoints(:,1);
splineyundist(:,i)=undistortedPoints(:,2);
clear undistortedPoints
end

writematrix(splineyundist,(sprintf('%s_y_splined.csv',filename)))
writematrix(splinexundist,(sprintf('%s_x_splined.csv',filename)))

ans='Step 5 complete!'

%% Step 6- Midline Analyzer
% This batch of code will produce all tthe kinematic variables you need!

%If this is the first time you're analyzing this video, run this line:
KineExport = MidlineAnalyser.createKineExport(filename, skip, framerate);

%If you already have KineExport for this video start at line 16
[KineExport, bpa] = MidlineAnalyser.getPointAnalysis(KineExport, 1, npts=10000); %Nose
[KineExport, bpa] = MidlineAnalyser.getPointAnalysis(KineExport, 18, npts=10000); %Pectoral girdle

[KineExport, bpa] = MidlineAnalyser.getPointAnalysis(KineExport, 34, npts=10000); %Mid-trunk
[KineExport, bpa] = MidlineAnalyser.getPointAnalysis(KineExport, 51, npts=10000); %Pelvic girdle
[KineExport, bpa] = MidlineAnalyser.getPointAnalysis(KineExport, 100, npts=10000); %Tail

[KineExport, wvspd118] = MidlineAnalyser.calculateWaveSpeed(KineExport, 1, 18);
[KineExport, wvspd1851] = MidlineAnalyser.calculateWaveSpeed(KineExport, 18, 51);
[KineExport, wvspd51100] = MidlineAnalyser.calculateWaveSpeed(KineExport, 51, 100);

MidlineAnalyser.save(KineExport, sprintf('%s_KineExport',filename), 'KineExport'); 

ans= 'Step 6 complete!'