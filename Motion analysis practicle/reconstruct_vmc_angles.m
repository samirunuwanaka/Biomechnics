%% Reconstruct Visual Motion Capture joint-angle outputs in MATLAB
% Input: VMC_joint_angles.csv exported from the Visual Motion Capture system.
% Required data: time in seconds, left-knee angle in degrees, left-ankle angle
% in degrees. The column names may be e.g. Time_s, Left Knee Angle (deg),
% Left Ankle Angle (deg); this script searches the column labels.
%
% The angle values are not recalculated from marker positions. This script
% reconstructs/plots the angle trajectories supplied by the VMC system and
% calculates angular velocity and acceleration from those angle traces.

clear; clc; close all;
inputFile = 'VMC_joint_angles.csv';
outputDir = 'matlab_angle_outputs';
if ~isfolder(outputDir), mkdir(outputDir); end

if ~isfile(inputFile)
    error(['Could not find %s. Export the angle time series from the Visual ', ...
           'Motion Capture system as a CSV with time in seconds and knee/ankle ', ...
           'angles in degrees, then place it beside this script.'], inputFile);
end

T = readtable(inputFile, 'VariableNamingRule', 'preserve');
rawNames = string(T.Properties.VariableNames);
normNames = lower(regexprep(rawNames, '[^a-zA-Z0-9]', ''));

% Identify columns without assuming the software's exact punctuation.
timeIdx = find(contains(normNames, 'time') & ~contains(normNames, 'timestamp'), 1);
if isempty(timeIdx), timeIdx = find(contains(normNames, 'time'), 1); end
kneeIdx = find(contains(normNames, 'knee') & contains(normNames, 'angle'), 1);
ankleIdx = find(contains(normNames, 'ankle') & contains(normNames, 'angle'), 1);
if isempty(timeIdx) || isempty(kneeIdx) || isempty(ankleIdx)
    error('Required columns not identified. Found columns: %s', strjoin(rawNames, ', '));
end

time_s = double(T{:, timeIdx});
knee_deg = double(T{:, kneeIdx});
ankle_deg = double(T{:, ankleIdx});

% Drop rows with missing/nonfinite values while retaining the recorded time.
valid = isfinite(time_s) & isfinite(knee_deg) & isfinite(ankle_deg);
time_s = time_s(valid); knee_deg = knee_deg(valid); ankle_deg = ankle_deg(valid);
if numel(time_s) < 3
    error('At least three valid samples are required to calculate derivatives.');
end
if any(diff(time_s) <= 0)
    error('The time column must be strictly increasing and expressed in seconds.');
end

% Numerical derivatives with the actual time vector (supports nonuniform time).
kneeVel = gradient(knee_deg, time_s);
kneeAcc = gradient(kneeVel, time_s);
ankleVel = gradient(ankle_deg, time_s);
ankleAcc = gradient(ankleVel, time_s);

% Summary statistics preserve the VMC angle convention.
Joint = ["Left knee"; "Left ankle"];
AngleMin_deg = [min(knee_deg); min(ankle_deg)];
AngleMax_deg = [max(knee_deg); max(ankle_deg)];
ROM_deg = AngleMax_deg - AngleMin_deg;
PeakAbsAngularVelocity_deg_s = [max(abs(kneeVel)); max(abs(ankleVel))];
PeakAngularVelocityTime_s = [time_s(find(abs(kneeVel)==max(abs(kneeVel)),1)); ...
                             time_s(find(abs(ankleVel)==max(abs(ankleVel)),1))];
PeakAbsAngularAcceleration_deg_s2 = [max(abs(kneeAcc)); max(abs(ankleAcc))];
PeakAngularAccelerationTime_s = [time_s(find(abs(kneeAcc)==max(abs(kneeAcc)),1)); ...
                                 time_s(find(abs(ankleAcc)==max(abs(ankleAcc)),1))];
summary = table(Joint, AngleMin_deg, AngleMax_deg, ROM_deg, ...
    PeakAbsAngularVelocity_deg_s, PeakAngularVelocityTime_s, ...
    PeakAbsAngularAcceleration_deg_s2, PeakAngularAccelerationTime_s);
writetable(summary, fullfile(outputDir, 'vmc_joint_angle_summary.csv'));

% Joint-angle time histories.
f = figure('Color','w','Name','VMC Joint Angles');
plot(time_s, knee_deg, 'LineWidth', 1.3); hold on;
plot(time_s, ankle_deg, 'LineWidth', 1.3);
grid on; xlabel('Time (s)'); ylabel('Angle (degrees)');
title('Visual Motion Capture joint-angle time histories');
legend('Left knee','Left ankle','Location','best');
exportgraphics(f, fullfile(outputDir, 'vmc_joint_angles_time.png'), 'Resolution', 220);

% Angular velocity histories.
f = figure('Color','w','Name','VMC Angular Velocities');
plot(time_s, kneeVel, 'LineWidth', 1.1); hold on;
plot(time_s, ankleVel, 'LineWidth', 1.1);
grid on; xlabel('Time (s)'); ylabel('Angular velocity (degrees/s)');
title('Angular velocity calculated from VMC angle outputs');
legend('Left knee','Left ankle','Location','best');
exportgraphics(f, fullfile(outputDir, 'vmc_joint_angular_velocity.png'), 'Resolution', 220);

% Angular acceleration histories.
f = figure('Color','w','Name','VMC Angular Accelerations');
plot(time_s, kneeAcc, 'LineWidth', 1.1); hold on;
plot(time_s, ankleAcc, 'LineWidth', 1.1);
grid on; xlabel('Time (s)'); ylabel('Angular acceleration (degrees/s^2)');
title('Angular acceleration calculated from VMC angle outputs');
legend('Left knee','Left ankle','Location','best');
exportgraphics(f, fullfile(outputDir, 'vmc_joint_angular_acceleration.png'), 'Resolution', 220);

disp('VMC angle summary:');
disp(summary);
fprintf('Outputs written to: %s\n', outputDir);
