import React, { useState, useEffect } from 'react';
const { ipcRenderer } = window.require('electron');

function LoginSignup() {
  const [rgbImageSrc, setRgbImageSrc] = useState('');
  const [depthImageSrc, setDepthImageSrc] = useState('');

  useEffect(() => {
    ipcRenderer.on('frame-data', (event, frameData) => {
      if (frameData.rgb) {
        setRgbImageSrc(`data:image/jpeg;base64,${frameData.rgb}`);
      }
      if (frameData.depth) {
        setDepthImageSrc(`data:image/jpeg;base64,${frameData.depth}`);
      }
    });

    // Clean up the listener when the component unmounts
    return () => {
      ipcRenderer.removeAllListeners('frame-data');
    };
  }, []);

  const handleStartServer = () => {
    ipcRenderer.send('save-command', 'start-stream');
  };

  const handleStopServer = () => {
    ipcRenderer.send('save-command', 'stop-stream');
  };

  const handleSaveCommand = (command) => {
    ipcRenderer.send('save-command', command);
    alert('Command sent successfully!');
  };

  return (
    <div className="flex flex-col w-full p-0 m-0" style={{fontWeight:"bold"}}>
      <h2>RealSense Frames Display</h2>
      <button onClick={handleStartServer}>Start Server</button>
      <button onClick={handleStopServer}>Stop Server</button>
      <div id="container">
        <div id="rgb-container">
          <img src={rgbImageSrc} alt="RGB Frame" />
        </div>
        <div id="depth-container">
          <img src={depthImageSrc} alt="Depth Frame" />
        </div>
      </div>

      {/* Add more buttons for other commands */}
      <button style={{background:"grey"}} onClick={() => handleSaveCommand('front')}>Front</button>
      <button  onClick={() => handleSaveCommand('back')}>back</button>
      <button style={{background:"grey"}} onClick={() => handleSaveCommand('side')}>side</button>
      <button  onClick={() => handleSaveCommand('rom_ha_left')}>rom_ha_left</button>
      <button style={{background:"grey"}} onClick={() => handleSaveCommand('rom_ha_right')}>rom_ha_right</button>
      <button  onClick={() => handleSaveCommand('rom_hf_left')}>rom_hf_left</button>
      <button style={{background:"grey"}} onClick={() => handleSaveCommand('rom_hf_right')}>rom_hf_right</button>

      <button onClick={() => handleSaveCommand('rom_sa_left')}>rom_sa_left</button>
      <button style={{background:"grey"}} onClick={() => handleSaveCommand('rom_sa_left')}>rom_sa_left</button>
      <button onClick={() => handleSaveCommand('rom_sa_left')}>rom_sa_left</button>
      <button style={{background:"grey"}}onClick={() => handleSaveCommand('rom_sa_left')}>rom_sa_left</button>



      {/* ... other buttons */}
    </div>
  );
}

export default LoginSignup;
