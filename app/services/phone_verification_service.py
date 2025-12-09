"""
Phone Verification Service
Handles OTP generation and verification for phone numbers
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import session


class PhoneVerificationService:
    """Service for phone verification using OTP"""
    
    OTP_SESSION_KEY = 'phone_verification'
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=self.OTP_LENGTH))
    
    def send_otp(self, phone: str) -> Dict[str, Any]:
        """
        Send OTP to phone number.
        In production, integrate with SMS gateway (Twilio, Kavenegar, etc.)
        For now, returns OTP in response (for development/testing)
        """
        # Normalize phone number (remove spaces, dashes, etc.)
        normalized_phone = ''.join(filter(str.isdigit, phone))
        
        # Generate OTP
        otp = self.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        
        # Store in session
        session[self.OTP_SESSION_KEY] = {
            'phone': normalized_phone,
            'otp': otp,
            'expires_at': expires_at.isoformat(),
            'attempts': 0,
            'max_attempts': 5
        }
        session.modified = True
        
        # In production, send SMS here:
        # sms_gateway.send_sms(phone, f"کد تایید شما: {otp}")
        
        # For development, return OTP in response
        return {
            'success': True,
            'message': 'کد تایید ارسال شد',
            'otp': otp,  # Remove this in production
            'expires_in_minutes': self.OTP_EXPIRY_MINUTES
        }
    
    def verify_otp(self, phone: str, otp: str):
        """
        Verify OTP for phone number.
        Returns (success, message)
        """
        verification_data = session.get(self.OTP_SESSION_KEY)
        
        if not verification_data:
            return False, "کد تایید یافت نشد. لطفا دوباره درخواست کنید."
        
        # Check phone match
        normalized_phone = ''.join(filter(str.isdigit, phone))
        if verification_data.get('phone') != normalized_phone:
            return False, "شماره تلفن مطابقت ندارد."
        
        # Check expiry
        expires_at = datetime.fromisoformat(verification_data['expires_at'])
        if datetime.utcnow() > expires_at:
            session.pop(self.OTP_SESSION_KEY, None)
            return False, "کد تایید منقضی شده است. لطفا دوباره درخواست کنید."
        
        # Check attempts
        attempts = verification_data.get('attempts', 0)
        max_attempts = verification_data.get('max_attempts', 5)
        if attempts >= max_attempts:
            session.pop(self.OTP_SESSION_KEY, None)
            return False, "تعداد تلاش‌های مجاز تمام شده است. لطفا دوباره درخواست کنید."
        
        # Verify OTP
        if verification_data.get('otp') != otp:
            verification_data['attempts'] = attempts + 1
            session[self.OTP_SESSION_KEY] = verification_data
            session.modified = True
            remaining = max_attempts - (attempts + 1)
            return False, f"کد تایید اشتباه است. {remaining} تلاش باقی مانده."
        
        # Success - mark as verified
        verification_data['verified'] = True
        verification_data['verified_at'] = datetime.utcnow().isoformat()
        session[self.OTP_SESSION_KEY] = verification_data
        session.modified = True
        
        return True, "تایید موفقیت‌آمیز بود."
    
    def is_phone_verified(self, phone: str) -> bool:
        """Check if phone number is verified in current session"""
        verification_data = session.get(self.OTP_SESSION_KEY)
        if not verification_data:
            return False
        
        normalized_phone = ''.join(filter(str.isdigit, phone))
        return (
            verification_data.get('phone') == normalized_phone and
            verification_data.get('verified', False) is True
        )
    
    def clear_verification(self):
        """Clear verification data from session"""
        session.pop(self.OTP_SESSION_KEY, None)
        session.modified = True

