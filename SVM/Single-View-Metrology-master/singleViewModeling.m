
function varargout = singleViewModeling(varargin)
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @singleViewModeling_OpeningFcn, ...
                   'gui_OutputFcn',  @singleViewModeling_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT



% --- Executes just before singleViewModeling is made visible.
function singleViewModeling_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to singleViewModeling (see VARARGIN)

% Choose default command line output for singleViewModeling
handles.output = hObject;
handles.scale = 1;
set(handles.imageView,'xtick',[]);
set(handles.imageView,'ytick',[]);
addpath('stlwrite');
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes singleViewModeling wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = singleViewModeling_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


%select points munally and calculate vanishing point 
function [x,y] = getVanishingPt(color)
global plots;
disp('Set at least two lines for vanishing point')
lines = zeros(3, 0);
while 1
    disp('Click first point or press q to stop')
    [x1,y1,b] = ginput(1);    
    if b=='q'        
        break;
    end
    disp('Click second point:');
    [x2,y2] = ginput(1);
    plots(size(plots,2)+1) = plot([x1 x2], [y1 y2], color,'LineWidth',2);
    lines(:, end+1) = real(cross([x1 y1 1]', [x2 y2 1]'));
end

% compute vp (3x1 vector in homogeneous coordinates)    
M = zeros(3,3);
for i = 1: size(lines,2)
    M(1,1) = M(1,1)+lines(1,i)*lines(1,i);
    M(1,2) = M(1,2)+lines(1,i)*lines(2,i);
    M(1,3) = M(1,3)+lines(1,i)*lines(3,i);
    M(2,1) = M(2,1)+lines(1,i)*lines(2,i);
    M(2,2) = M(2,2)+lines(2,i)*lines(2,i);
    M(2,3) = M(2,3)+lines(2,i)*lines(3,i);
    M(3,1) = M(3,1)+lines(1,i)*lines(3,i);
    M(3,2) = M(3,2)+lines(2,i)*lines(3,i);
    M(3,3) = M(3,3)+lines(3,i)*lines(3,i);    
end
[vp,~] = eigs(M,1,'SM');
x = vp(1)/vp(3);
y = vp(2)/vp(3);


% --- Executes on button press in startCalc.
function startCalc_Callback(hObject, eventdata, handles)
% hObject    handle to startCalc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global plots;
if ~handles.vX
    msgbox('Initial information not complete!');
elseif ~handles.refX
    msgbox('Initial information not complete!');
else
delete(plots(:));
plots = [];

% scaling factor
a_x = ((handles.vX - handles.refX) \ (handles.refX - handles.O))/handles.refXlen
a_y = ((handles.vY - handles.refY) \ (handles.refY - handles.O))/handles.refYlen
a_z = ((handles.vZ - handles.refZ) \ (handles.refZ - handles.O))/handles.refZlen

% Projection Matrix P
handles.P = [handles.vX * a_x, handles.vY * a_y, handles.vZ * a_z, handles.O];
ProjectionMatrix = handles.P %display
P  = handles.P;
P = [P(:,1) -P(:,2) -P(:,3) P(:,4)];

% Homography Matrix H
handles.Hxy = [P(:,1:2),P(:,4)];
handles.Hxz = [P(:,1),P(:,3:4)];
handles.Hyz = P(:,2:4);
Hxy = handles.Hxy
Hxz = handles.Hxz
Hyz = handles.Hyz
guidata(hObject, handles);

end


% --------------------------------------------------------------------
function openfile_ClickedCallback(hObject, eventdata, handles)
% hObject    handle to openfile (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global plots;
global filename;
  [filename1,filepath1]=uigetfile({'*.*','All Files'},'Select File');
  if filename1
      filename = filename1;
      addpath(filepath1);
      handles.g = imread(filename1);
      axes(handles.imageView);
      hold all;
      %xlim([-1 2.5*handles.width]);
      %ylim([-1 2.5*handles.height]);
      delete(get(gca,'Children'));
      imshow(handles.g);
      plots = [];
      guidata(hObject, handles);
  end

  
% --------------------------------------------------------------------
function savefile_ClickedCallback(hObject, eventdata, handles)
% hObject    handle to savefile (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



% --- Executes on button press in saveVP.
function saveVP_Callback(hObject, eventdata, handles)
% hObject    handle to saveVP (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
vX = handles.vX; 
vY = handles.vY; 
vZ = handles.vZ;
save('VP_sony.mat', 'vX', 'vY', 'vZ');
disp('vanishing points saved');

% --- Executes on button press in loadVP.
function loadVP_Callback(hObject, eventdata, handles)
% hObject    handle to loadVP (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
load('VP_sony.mat', 'vX', 'vY', 'vZ');
handles.vX = vX; 
handles.vY = vY; 
handles.vZ = vZ;
disp('vanishing points loaded');
guidata(hObject, handles);


% --- Executes on button press in getOrigin.
function getOrigin_Callback(hObject, eventdata, handles)
% hObject    handle to getOrigin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global plots;
disp('Select the origin');
[x,y] = ginput(1);
plots(size(plots,2)+1) = plot(x,y,'o');
handles.O = [x;y;1];
guidata(hObject, handles);


function transformHelper(invH, im, height, width)
% maketform - imtransform / projective2d - imwarp
%im = imcrop(im);
invH = invH';
tform = projective2d(invH);
B = imwarp(im, tform);
warning('off', 'Images:initSize:adjustingMag');
figure,[I2, rect] = imcrop(B); 

delete(get(gca,'Children'));
imshow(I2);



% --- Executes on selection change in drawPLines.
function drawPLines_Callback(hObject, eventdata, handles)
% hObject    handle to drawPLines (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns drawPLines contents as cell array
%        contents{get(hObject,'Value')} returns selected item from drawPLines
handles = guidata(hObject);
str = get(hObject, 'String');
val = get(hObject,'Value');
switch str{val}
    case 'X'
        [x,y]= getVanishingPt('r');
        handles.vX = [x;y;1];
    case 'Y'
        [x,y]= getVanishingPt('g');
        handles.vY = [x;y;1];
    case 'Z'
        [x,y]= getVanishingPt('b');
        handles.vZ = [x;y;1];
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function drawPLines_CreateFcn(hObject, eventdata, handles)
% hObject    handle to drawPLines (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in setReference.
function setReference_Callback(hObject, eventdata, handles)
% hObject    handle to setReference (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns setReference contents as cell array
%        contents{get(hObject,'Value')} returns selected item from setReference
global plots;
handles = guidata(hObject);
str = get(hObject, 'String');
val = get(hObject,'Value');
if ~handles.O
    msgbox('Select the Origin first!');
else
    switch str{val}
        case 'X'
            disp('Select the refrence point in X direction');
            [x,y] = ginput(1);
            plots(size(plots,2)+1) = plot(x,y,'*');
            plots(size(plots,2)+1) = plot([x handles.O(1)],[y handles.O(2)]);
            handles.refX = [x;y;1];
            answer = inputdlg('Enter reference length','Reference Length',[1 30],{'0'});
            %insertText(get(gca,'Children'),[(x+handles.O(1))/2 (y+handles.O(2))/2], answer);
            text(x,y,answer,'FontSize',14,'Color','red');
            handles.refXlen = str2double(answer);
        case 'Y'
            disp('Select the refrence point in Y direction');
            [x,y] = ginput(1);
            plots(size(plots,2)+1) = plot(x,y,'*');
            plots(size(plots,2)+1) = plot([x handles.O(1)],[y handles.O(2)]);
            handles.refY = [x;y;1];
            answer = inputdlg('Enter reference length','Reference Length',[1 30],{'0'});
            %insertText(get(gca,'Children'),[(x+handles.O(1))/2 (y+handles.O(2))/2], answer);
            text(x,y,answer,'FontSize',14,'Color','red');
            handles.refYlen = str2double(answer);
        case 'Z'
            disp('Select the refrence point in Z direction');
            [x,y] = ginput(1);
            plots(size(plots,2)+1) = plot(x,y,'*');
            plots(size(plots,2)+1) = plot([x handles.O(1)],[y handles.O(2)]);
            handles.refZ = [x;y;1];
            answer = inputdlg('Enter reference length','Reference Length',[1 30],{'0'});
            %insertText(get(gca,'Children'),[(x+handles.O(1))/2 (y+handles.O(2))/2], answer);
            text(x,y,answer,'FontSize',14,'Color','red');
            handles.refZlen = str2double(answer);
    end
end
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function setReference_CreateFcn(hObject, eventdata, handles)
% hObject    handle to setReference (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in transform.
function transform_Callback(hObject, eventdata, handles)
% hObject    handle to transform (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns transform contents as cell array
%        contents{get(hObject,'Value')} returns selected item from transform
handles = guidata(hObject);
str = get(hObject, 'String');
val = get(hObject,'Value');

if ~handles.P
        msgbox('Click START to do calculation first!');
else
    im = handles.g;
    
    height = size(im, 1);
    width = size(im, 2);

    switch str{val}
        case 'X-Y'
            invH = inv(handles.Hxy);
            disp('X-Y plane');
            transformHelper(invH, im, height, width);
        case 'Y-Z'
            invH = inv(handles.Hyz);
            disp('Y-Z plane');
            transformHelper(invH, im, height, width);
        case 'X-Z'
            invH = inv(handles.Hxz);
            disp('X-Z plane');
            transformHelper(invH, im, height, width);
    end
    
    guidata(hObject, handles);
end


% --- Executes during object creation, after setting all properties.
function transform_CreateFcn(hObject, eventdata, handles)
% hObject    handle to transform (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in selectIP.
function selectIP_Callback(hObject, eventdata, handles)
% hObject    handle to selectIP (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global plots;
handles.ThreeDpos = zeros(3,0);
b0 = handles.O
t0 = handles.refZ
H = handles.refZlen

horizon = real(cross(handles.vY, handles.vX))
length = sqrt(horizon(1)^2 + horizon(2)^2)
horizon = horizon/length

while 1
    disp('Click a base point or press q to stop')
    [x1,y1,b] = ginput(1)    
    if b=='q'        
        break;
    end
    plots(size(plots,2)+1) = plot(x1,y1,'*');
    b = [x1;y1;1]
    
    disp('Click an interesting point');
    [x2,y2] = ginput(1)
    plots(size(plots,2)+1) = plot(x2,y2,'*');
    r = [x2;y2;1]
    
    line1 = real(cross(b0, b))
    v = real(cross(line1, horizon))
    v = v/v(3)

    line2 = real(cross(v', t0))
    vertical_line = real(cross(r, b))
    t = real(cross(line2, vertical_line))
    t = t/t(3)
    height = H*sqrt(sumsqr(r-b))*sqrt(sumsqr(handles.vZ'-t))/...
        sqrt(sumsqr(t'-b))/sqrt(sumsqr(handles.vZ-r))

end
guidata(hObject, handles);


% --- Executes on button press in SaveAll.
function SaveAll_Callback(hObject, eventdata, handles)
% hObject    handle to SaveAll (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
vX = handles.vX
vY = handles.vY
vZ = handles.vZ

%Origin 
Origin = handles.O

%reference coordinate of X-O, Y-O, Z-O
X_O = handles.refX 
Y_O = handles.refY
Z_O = handles.refZ

%reference length 
len_X_O = handles.refXlen
len_Y_O = handles.refYlen
len_Z_O = handles.refZlen

% scaling factor
a_x = ((handles.vX - handles.refX) \ (handles.refX - handles.O))/handles.refXlen;
a_y = ((handles.vY - handles.refY) \ (handles.refY - handles.O))/handles.refYlen;
a_z = ((handles.vZ - handles.refZ) \ (handles.refZ - handles.O))/handles.refZlen;

scale_X = a_x 
scale_Y = a_y
scale_Z = a_z

% Projection Matrix P
handles.P = [handles.vX * a_x, handles.vY * a_y, handles.vZ * a_z, handles.O];
ProjectionMatrix = handles.P

% Homography Matrix H
P  = handles.P;
P = [P(:,1) -P(:,2) -P(:,3) P(:,4)];
handles.Hxy = [P(:,1:2),P(:,4)];
handles.Hxz = [P(:,1),P(:,3:4)];
handles.Hyz = P(:,2:4);

Hxy = handles.Hxy
Hxz = handles.Hxz
Hyz = handles.Hyz

global filename;
VARIABLES = filename;
VARIABLES = VARIABLES(1:end-4)

file_name = sprintf('All_Parameters_%s.mat',VARIABLES)
save(file_name, 'vX', 'vY', 'vZ','Origin','X_O','Y_O','Z_O','len_X_O','len_Y_O','len_Z_O','scale_X','scale_Y','scale_Z','ProjectionMatrix','Hxy','Hxz','Hyz');
disp('All Parameters saved');


% --- Executes on button press in LoadAll.
function LoadAll_Callback(hObject, eventdata, handles)
% hObject    handle to LoadAll (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

global filename;
VARIABLES = filename;
VARIABLES = VARIABLES(1:end-4)

file_name = sprintf('All_Parameters_%s.mat',VARIABLES)
load(file_name,'vX', 'vY', 'vZ','Origin','X_O','Y_O','Z_O','len_X_O','len_Y_O','len_Z_O','scale_X','scale_Y','scale_Z','ProjectionMatrix','Hxy','Hxz','Hyz');

handles.vX = vX;
handles.vY = vY;
handles.vZ = vZ;

handles.O = Origin;

handles.refX = X_O;
handles.refY = Y_O;
handles.refZ = Z_O;

handles.refXlen = len_X_O; 
handles.refYlen = len_Y_O; 
handles.refZlen = len_Z_O;

% scaling factor
a_x = scale_X; 
a_y = scale_Y;
a_z = scale_Z; 

% Projection Matrix P
handles.P = ProjectionMatrix;

% Homography Matrix H
handles.Hxy = Hxy;
handles.Hxz = Hxz;
handles.Hyz = Hyz;

disp('all parameters loaded');
guidata(hObject, handles);
