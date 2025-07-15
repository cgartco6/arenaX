/* Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Orbitron', sans-serif;
}

body {
    background: #0a0e17;
    color: #e0e0ff;
    overflow: hidden;
    height: 100vh;
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(25, 49, 85, 0.3) 0%, transparent 20%),
        radial-gradient(circle at 90% 80%, rgba(67, 28, 83, 0.3) 0%, transparent 20%);
}

#loading-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: #0a0e17;
    position: absolute;
    width: 100%;
    z-index: 1000;
}

.loader {
    border: 8px solid #1a1f2d;
    border-top: 8px solid #6a3dff;
    border-radius: 50%;
    width: 80px;
    height: 80px;
    animation: spin 1.5s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.progress-bar {
    width: 300px;
    height: 20px;
    background: #1a1f2d;
    border-radius: 10px;
    margin-top: 20px;
    overflow: hidden;
}

.progress {
    height: 100%;
    background: linear-gradient(90deg, #6a3dff, #8a5eff);
    border-radius: 10px;
    width: 0%;
    transition: width 0.3s ease;
}

/* Game Container */
#game-container {
    position: relative;
    width: 100%;
    height: 100vh;
}

#unity-container {
    position: absolute;
    width: 100%;
    height: 100%;
}

#unity-canvas {
    width: 100%;
    height: 100%;
    background: #0a0e17;
}

/* Game UI */
#game-ui {
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    z-index: 10;
}

#player-stats {
    background: rgba(10, 14, 23, 0.8);
    border: 1px solid #2a2f4d;
    border-radius: 10px;
    padding: 15px;
    display: flex;
    gap: 20px;
    backdrop-filter: blur(5px);
}

.stat {
    display: flex;
    flex-direction: column;
    min-width: 120px;
}

.label {
    font-size: 12px;
    color: #8a9bb8;
    text-transform: uppercase;
    margin-bottom: 5px;
}

#player-level, #player-credits {
    font-size: 24px;
    font-weight: bold;
    color: #6a3dff;
}

.bar {
    width: 200px;
    height: 20px;
    background: #1a1f2d;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 5px;
}

.fill {
    height: 100%;
    background: linear-gradient(90deg, #ff3d71, #ff6a8d);
    border-radius: 10px;
    width: 100%;
}

.button {
    background: linear-gradient(135deg, #6a3dff, #8a5eff);
    border: none;
    border-radius: 8px;
    padding: 12px 25px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 15px rgba(106, 61, 255, 0.3);
}

.button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(106, 61, 255, 0.5);
}

.button img {
    width: 24px;
    height: 24px;
}

/* Modals */
.modal {
    display: none;
    position: fixed;
    z-index: 20;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(5px);
}

.modal-content {
    background: #151b2b;
    margin: 5% auto;
    padding: 30px;
    border: 1px solid #2a2f4d;
    border-radius: 15px;
    width: 80%;
    max-width: 900px;
    position: relative;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.close {
    position: absolute;
    right: 25px;
    top: 20px;
    color: #8a9bb8;
    font-size: 30px;
    font-weight: bold;
    cursor: pointer;
    transition: color 0.2s;
}

.close:hover {
    color: #ff3d71;
}

/* Shop */
.shop-categories {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

.category {
    background: #1a2135;
    border: none;
    padding: 12px 20px;
    border-radius: 6px;
    color: #8a9bb8;
    cursor: pointer;
    transition: all 0.2s;
}

.category.active, .category:hover {
    background: linear-gradient(135deg, #6a3dff, #8a5eff);
    color: white;
}

.shop-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.shop-item {
    background: #1a2135;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #2a2f4d;
    transition: transform 0.3s;
}

.shop-item:hover {
    transform: translateY(-5px);
    border-color: #6a3dff;
}

.item-image {
    height: 120px;
    background: #0f1422;
    display: flex;
    align-items: center;
    justify-content: center;
}

.item-image img {
    max-width: 80%;
    max-height: 80%;
}

.item-info {
    padding: 15px;
}

.item-name {
    font-size: 16px;
    margin-bottom: 5px;
    color: #e0e0ff;
}

.item-price {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #ffd166;
    font-weight: bold;
}

.buy-button {
    background: linear-gradient(135deg, #ff9a3d, #ffbd6a);
    border: none;
    border-radius: 5px;
    color: #151b2b;
    padding: 8px 15px;
    margin-top: 10px;
    cursor: pointer;
    width: 100%;
    font-weight: bold;
    transition: opacity 0.2s;
}

.buy-button:hover {
    opacity: 0.9;
}

/* Battle Pass */
.pass-container {
    display: flex;
    gap: 30px;
    margin-top: 20px;
}

.free-pass, .premium-pass {
    flex: 1;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #2a2f4d;
}

.free-pass {
    background: #1a2135;
}

.premium-pass {
    background: linear-gradient(135deg, #1a2135, #2a1a35);
    border: 1px solid #6a3dff;
    position: relative;
    overflow: hidden;
}

.premium-pass::before {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: rgba(106, 61, 255, 0.1);
    border-radius: 50%;
    transform: translate(40%, -40%);
}

.badge {
    background: #ffd166;
    color: #151b2b;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 14px;
    margin-left: 5px;
}

.rewards {
    margin-top: 15px;
}

.reward {
    padding: 10px;
    border-bottom: 1px solid #2a2f4d;
}

.reward:last-child {
    border-bottom: none;
}

#buy-pass-button {
    background: linear-gradient(135deg, #6a3dff, #8a5eff);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 12px 25px;
    margin-top: 20px;
    cursor: pointer;
    width: 100%;
    font-weight: bold;
    font-size: 16px;
    transition: transform 0.2s;
}

#buy-pass-button:hover {
    transform: translateY(-3px);
}

/* Tournament Banner */
#tournament-banner {
    position: absolute;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #1a2135, #2a1a35);
    border: 1px solid #6a3dff;
    border-radius: 10px;
    padding: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
    z-index: 10;
    max-width: 400px;
    backdrop-filter: blur(5px);
    box-shadow: 0 5px 20px rgba(106, 61, 255, 0.3);
}

.sponsor-logo {
    width: 80px;
    height: 80px;
    background: #2a2f4d;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: #8a9bb8;
}

#tournament-banner .info {
    flex: 1;
}

#tournament-banner h3 {
    color: #ffd166;
    margin-bottom: 5px;
    font-size: 18px;
}

#tournament-banner p {
    color: #8a9bb8;
    font-size: 14px;
    margin-bottom: 10px;
}

#join-tournament {
    background: linear-gradient(135deg, #ff3d71, #ff6a8d);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 8px 15px;
    cursor: pointer;
    font-weight: bold;
    transition: opacity 0.2s;
}

#join-tournament:hover {
    opacity: 0.9;
}

/* Unity Loading Bar */
#unity-loading-bar {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 10px;
    background: #1a1f2d;
    border-radius: 5px;
    overflow: hidden;
}

#unity-progress-bar-empty {
    width: 100%;
    height: 100%;
}

#unity-progress-bar-full {
    width: 0%;
    height: 100%;
    background: linear-gradient(90deg, #6a3dff, #8a5eff);
    transition: width 0.3s;
}
