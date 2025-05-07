/**
 * Service for handling WebRTC connections
 */
class WebRTCService {
    constructor() {
      this.peerConnection = null;
      this.localStream = null;
      this.remoteStream = null;
      this.socket = null;
      this.sessionId = null;
      this.role = null;
      this.onRemoteStreamCallback = null;
      this.onConnectionStateChangeCallback = null;
    }
  
    /**
     * Initialize WebRTC connection
     * @param {string} sessionId - The interview session ID
     * @param {string} role - Either "interviewer" or "candidate"
     * @param {MediaStream} localStream - The local media stream
     * @param {Function} onRemoteStream - Callback for when remote stream is received
     * @param {Function} onConnectionStateChange - Callback for connection state changes
     */
    async initialize(sessionId, role, localStream, onRemoteStream, onConnectionStateChange) {
      this.sessionId = sessionId;
      this.role = role;
      this.localStream = localStream;
      this.onRemoteStreamCallback = onRemoteStream;
      this.onConnectionStateChangeCallback = onConnectionStateChange;
      
      // Create a new remote stream
      this.remoteStream = new MediaStream();
      if (this.onRemoteStreamCallback) {
        this.onRemoteStreamCallback(this.remoteStream);
      }
      
      // Setup WebSocket connection
      this.setupSignaling();
      
      // Create and configure RTCPeerConnection
      await this.setupPeerConnection();
    }
  
    /**
     * Set up WebSocket signaling
     */
    setupSignaling() {
      const wsUrl = `ws://localhost:8000/ws/interview/${this.sessionId}/${this.role}`;
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = () => {
        console.log('WebSocket connection established');
      };
      
      this.socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
          case 'offer':
            if (this.role === 'candidate') {
              await this.handleOffer(message.offer);
            }
            break;
            
          case 'answer':
            if (this.role === 'interviewer') {
              await this.handleAnswer(message.answer);
            }
            break;
            
          case 'ice-candidate':
            await this.handleIceCandidate(message.candidate);
            break;
            
          case 'user-disconnected':
            console.log(`${message.sender} disconnected`);
            // Handle remote user disconnect
            break;
        }
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }
  
    /**
     * Set up the RTCPeerConnection
     */
    async setupPeerConnection() {
      const configuration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      };
      
      this.peerConnection = new RTCPeerConnection(configuration);
      
      // Add local tracks to the connection
      this.localStream.getTracks().forEach(track => {
        this.peerConnection.addTrack(track, this.localStream);
      });
      
      // Handle ICE candidates
      this.peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.sendSignalingMessage({
            type: 'ice-candidate',
            candidate: event.candidate
          });
        }
      };
      
      // Handle connection state changes
      this.peerConnection.onconnectionstatechange = () => {
        if (this.onConnectionStateChangeCallback) {
          this.onConnectionStateChangeCallback(this.peerConnection.connectionState);
        }
      };
      
      // Handle incoming tracks
      this.peerConnection.ontrack = (event) => {
        event.streams[0].getTracks().forEach(track => {
          this.remoteStream.addTrack(track);
        });
      };
      
      // If interviewer, create and send offer
      if (this.role === 'interviewer') {
        await this.createAndSendOffer();
      }
    }
  
    /**
     * Create and send an offer
     */
    async createAndSendOffer() {
      try {
        const offer = await this.peerConnection.createOffer();
        await this.peerConnection.setLocalDescription(offer);
        
        this.sendSignalingMessage({
          type: 'offer',
          offer: offer
        });
      } catch (error) {
        console.error('Error creating offer:', error);
      }
    }
  
    /**
     * Handle an incoming offer
     * @param {RTCSessionDescriptionInit} offer - The received offer
     */
    async handleOffer(offer) {
      try {
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
        
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);
        
        this.sendSignalingMessage({
          type: 'answer',
          answer: answer
        });
      } catch (error) {
        console.error('Error handling offer:', error);
      }
    }
  
    /**
     * Handle an incoming answer
     * @param {RTCSessionDescriptionInit} answer - The received answer
     */
    async handleAnswer(answer) {
      try {
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
      } catch (error) {
        console.error('Error handling answer:', error);
      }
    }
  
    /**
     * Handle an incoming ICE candidate
     * @param {RTCIceCandidateInit} candidate - The received ICE candidate
     */
    async handleIceCandidate(candidate) {
      try {
        if (candidate) {
          await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        }
      } catch (error) {
        console.error('Error handling ICE candidate:', error);
      }
    }
  
    /**
     * Send a message through the signaling channel
     * @param {Object} message - The message to send
     */
    sendSignalingMessage(message) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify(message));
      } else {
        console.error('WebSocket not open, cannot send message');
      }
    }
  
    /**
     * Close the WebRTC connection
     */
    close() {
      if (this.peerConnection) {
        this.peerConnection.close();
        this.peerConnection = null;
      }
      
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    }
  }
  
  export default new WebRTCService();