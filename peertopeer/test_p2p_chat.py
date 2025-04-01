import unittest
from unittest.mock import MagicMock, patch
import socket
import threading
import io
import sys
import p2p_chat


class TestP2PChat(unittest.TestCase):

    @patch('socket.socket')
    def test_server_client_connection(self, mock_socket_class):
        mock_server_socket = MagicMock()
        mock_client_socket = MagicMock()

        # Set up the socket mock
        mock_socket_class.side_effect = [mock_server_socket, mock_client_socket]
        

        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 12345))

        
        mock_client_socket.recv.side_effect = [b"Hello from client", b""]

        
        with patch('builtins.input', side_effect=["Hi from server", KeyboardInterrupt()]):
            server_thread = threading.Thread(target=p2p_chat.run_server, args=(12345,), daemon=True)
            server_thread.start()

            
            server_thread.join(timeout=2)

     
        mock_server_socket.bind.assert_called_with(("0.0.0.0", 12345))
        mock_server_socket.listen.assert_called_once()

        
        mock_client_socket.sendall.assert_called_with(b"Hi from server")

    @patch('socket.socket')
    def test_client_sending_and_receiving(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

    
        mock_socket.recv.side_effect = [b"Hi from server", b""]

        with patch('builtins.input', side_effect=["Hello server", KeyboardInterrupt()]):
            client_thread = threading.Thread(target=p2p_chat.run_client, args=("127.0.0.1", 12345), daemon=True)
            client_thread.start()
            client_thread.join(timeout=2)

        mock_socket.connect.assert_called_with(("127.0.0.1", 12345))
        mock_socket.sendall.assert_called_with(b"Hello server")


if __name__ == '__main__':
    unittest.main()
