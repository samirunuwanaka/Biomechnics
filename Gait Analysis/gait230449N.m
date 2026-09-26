%% gait.m -- Starter file for the Gait Analysis practical
%  ME4270 / BM3500  Biomedical Engineering Applications
%
%  Keep this file and markers.csv in the same folder, make that folder the
%  Current Folder, and save this file as gait<index>.m before you edit it.
%  Fill in every TODO. The figure numbers match the lab sheet tasks.
%  One data point = 0.01 s (100 Hz). All coordinates are in mm.
%
%  Name: Nuwanaka WAS                        Index number: 230449N

clear all
close all

% Load the data into array A (marker data)
A = csvread('markers.csv');

% Number of rows (frames) and columns in A
[rA,cA] = size(A);

% Data point (frame) numbers
datapt = A(:,1);

% Right side markers. Each is rA x 3 = [x y z] in mm.
iliaca = A(:, 5: 7);    % anterior superior iliac spine (ASIS)
iliacp = A(:,11:13);    % posterior superior iliac spine (PSIS)
hip    = A(:,17:19);    % greater trochanter (TRO)
knee   = A(:,23:25);    % lateral femoral condyle (LFC)
ankle  = A(:,29:31);    % lateral malleolus (LMA)
toe    = A(:,35:37);    % metatarsal 2nd head (TOE)


%% Task 2 -- xz trajectories
figure(1)

% iliaca
plot(iliaca(:,1),iliaca(:,3))
hold on
text(iliaca(rA,1),iliaca(rA,3),'ILIACA')

% iliacp
plot(iliacp(:,1),iliacp(:,3))
hold on
text(iliacp(rA,1),iliacp(rA,3),'ILIACAP')

% hip
plot(hip(:,1),hip(:,3))
hold on
text(hip(rA,1),hip(rA,3),'ILIACAP')

% knee
plot(knee(:,1),knee(:,3))
hold on
text(knee(rA,1),knee(rA,3),'KNEE')

% ankle
plot(ankle(:,1),ankle(:,3))
hold on
text(ankle(rA,1),ankle(rA,3),'ANKLE')

% toe
plot(toe(:,1),toe(:,3))
text(toe(rA,1),toe(rA,3),'TOE')

axis('equal')
xlabel('x (mm)')
ylabel('z (mm)')

title('X-Z trajectories of each marker')


%% Task 3 -- xyz trajectories
figure(2)

scatter3(iliaca(:,1),iliaca(:,2),iliaca(:,3))
hold on
text(iliaca(rA,1),iliaca(rA,2),iliaca(rA,3),'ILIACA')

% iliacp
scatter3(iliacp(:,1),iliacp(:,2),iliacp(:,3))
hold on
text(iliacp(rA,1),iliacp(rA,2),iliacp(rA,3),'ILIACAP')

% hip
scatter3(hip(:,1),hip(:,2),hip(:,3))
hold on
text(hip(rA,1),hip(rA,2),hip(rA,3),'ILIACAP')

% knee
scatter3(knee(:,1),knee(:,2),knee(:,3))
hold on
text(knee(rA,1),knee(rA,2),knee(rA,3),'KNEE')

% ankle
scatter3(ankle(:,1),ankle(:,2),ankle(:,3))
hold on
text(ankle(rA,1),ankle(rA,2),ankle(rA,3),'ANKLE')

% toe
scatter3(toe(:,1),toe(:,2),toe(:,3))
text(toe(rA,1),toe(rA,2),toe(rA,3),'TOE')

axis('equal')
xlabel('x (mm)')
ylabel('y (mm)')
zlabel('z (mm)')

title('X-Y -Z trajectories of each marker')


%% Task 4 -- ankle and toe heights, gait events
figure(3)

% TODO: plot the z (height) of the ankle and of the toe against datapt
plot(datapt,ankle(:,3))
hold on
plot(datapt,toe(:,3))

xlabel('data point number')
ylabel('z (mm)')
legend("ANKLE","TOE")

% read the events off Figure 3 and type the data point numbers here
HS1 = 204;      % heel strike
FF  = 230;      % foot flat
HO  = 258;      % heel off
TO  = 276;      % toe off
HS2 = 314;      % next heel strike of the same foot

% label them on the figure, e.g.  text(HS1,90,'HEEL STRIKE')
text(HS1,90,'HEEL STRIKE','Rotation',90)
text(FF,90,'FOOT FLAT','Rotation',90)
text(HO,90,'HEEL OFF','Rotation',90)
text(TO,90,'TOE OFF','Rotation',90)
text(HS2,90,'HEEL STRIKE','Rotation',90)

% TODO: times in seconds (one data point = 0.01 s)
T_cycle  = HS2-HS1  % gait cycle time
T_stance = HO-HS1  % stance time
T_swing  = HS2-HO  % swing time

% TODO: stance and swing as a percentage of the gait cycle
P_stance = (T_stance / T_cycle) * 100
P_swing  = (T_swing / T_cycle) * 100


%% Task 5 -- stride length, cadence, average velocity
figure(4)
plot(datapt,ankle(:,1))       % read the ankle x at the two heel strikes
xlabel('data point number')
ylabel('ankle x (mm)')

figure(5)
plot(datapt,iliaca(:,1))      % read the pelvis x at the two heel strikes
xlabel('data point number')
ylabel('iliaca x (mm)')

% TODO: mm -> m, and remember one data point = 0.01 s
stride_length = 0;            % m
cadence       = 0;            % steps/min
v_avg         = 0;            % m/s


%% Task 6 -- instantaneous velocity of progression
figure(6)

% TODO: velocity = change in position / change in time
% inst_velocity = ((iliacp(2:rA,1)-iliacp(1:rA-1,1))/0.01)/1000;
% plot(datapt(1:rA-1),inst_velocity)

xlabel('data point number')
ylabel('instantaneous velocity (m/s)')


%% Task 7 -- thigh segment length in 2D and 3D
figure(7)

% TODO: distance between the hip marker and the knee marker.
% Keep the WHOLE sum inside sqrt( ):
% thigh_len_2D = sqrt( (hip(:,1)-knee(:,1)).^2 + ... );   % x and z
% thigh_len_3D = sqrt( ... );                             % x, y and z
% plot(datapt,thigh_len_2D)
% hold on
% plot(datapt,thigh_len_3D)

xlabel('data point number')
ylabel('thigh segment length (mm)')

% A thigh is about 440 mm. If your plot says 40000, check the brackets.


%% Task 8 -- knee joint angle in 2D
figure(8)

% Cosine rule on the triangle hip - knee - ankle, using x and z only:
%   a = thigh length, b = knee to ankle, c = hip to ankle
%   cos(theta) = (a^2 + b^2 - c^2) / (2ab),  knee angle = 180 - theta
% TODO
% thigh_len     = thigh_len_2D;
% leg_len       = sqrt( ... );
% hip_ankle_len = sqrt( ... );
% knee_angle    = 180 - acosd( ... );
% plot(datapt,knee_angle)

xlabel('data point number')
ylabel('knee angle (deg)')
