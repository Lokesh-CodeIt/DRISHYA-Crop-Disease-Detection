/**
 * AuthForm.jsx - DRISHYA Editorial Authentication Form
 *
 * Implements:
 * - Real Sign In & Create Account workflows with backend SQLite/JWT integration
 * - Calm, accessible validation feedback
 * - Show/Hide password toggle
 * - Form state persistence across language switching
 * - Minimum 48px touch targets and accessible focus rings
 */

import React, { useState } from 'react';
import { Eye, EyeOff, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';

export default function AuthForm({ onAuthenticated, className = '' }) {
  const { login, register, navigate } = useAuth();
  const { t, language } = useLanguage();

  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errorMsg) setErrorMsg(null);
  };

  const handleModeSwitch = (newMode) => {
    setMode(newMode);
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    const emailClean = formData.email.trim();
    const passwordClean = formData.password;

    if (!emailClean) {
      setErrorMsg(t('auth.email') + ' is required.');
      return;
    }

    if (!passwordClean || passwordClean.length < 6) {
      setErrorMsg(t('auth.password_too_short'));
      return;
    }

    const getTranslatedError = (err, defaultKey) => {
      const msg = err?.message || '';
      const status = err?.status;
      if (status === 409 || msg.includes('already exists')) {
        if (language === 'hi') return 'इस ईमेल पते से पहले से एक खाता मौजूद है।';
        if (language === 'mr') return 'या ईमेल पत्त्यावर आधीच खाते अस्तित्वात आहे.';
        return 'An account with this email address already exists.';
      }
      if (status === 401 || msg.includes('Invalid email') || msg.includes('Invalid credentials')) {
        if (language === 'hi') return 'अमान्य ईमेल या पासवर्ड। कृपया पुनः प्रयास करें।';
        if (language === 'mr') return 'अवैध ईमेल किंवा पासवर्ड. कृपया पुन्हा प्रयत्न करा.';
        return 'Invalid email or password. Please verify and try again.';
      }
      if (status === 400 && msg.includes('6 characters')) {
        return t('auth.password_too_short');
      }
      if (err?.status === 0 || msg.includes('Network') || msg.includes('fetch')) {
        return t('error.network');
      }
      return t(defaultKey);
    };

    if (mode === 'register') {
      const nameClean = formData.name.trim();
      if (!nameClean) {
        setErrorMsg(t('auth.name') + (language === 'hi' ? ' आवश्यक है।' : language === 'mr' ? ' आवश्यक आहे.' : ' is required.'));
        return;
      }
      if (passwordClean !== formData.confirmPassword) {
        setErrorMsg(t('auth.password_mismatch'));
        return;
      }

      setLoading(true);
      try {
        await register({
          name: nameClean,
          email: emailClean,
          password: passwordClean,
          preferred_language: language,
        });

        // Automatically log in after registration
        await login(emailClean, passwordClean);
        setSuccessMsg(t('auth.register_success'));
        if (onAuthenticated) onAuthenticated();
        else navigate('/home');
      } catch (err) {
        setErrorMsg(getTranslatedError(err, 'error.generic'));
      } finally {
        setLoading(false);
      }
    } else {
      // Sign In mode
      setLoading(true);
      try {
        await login(emailClean, passwordClean);
        setSuccessMsg(t('auth.login_success'));
        if (onAuthenticated) onAuthenticated();
        else navigate('/home');
      } catch (err) {
        setErrorMsg(getTranslatedError(err, 'error.unauthorized'));
      } finally {
        setLoading(false);
      }
    }
  };

  const isHindiOrMarathi = language === 'hi' || language === 'mr';

  return (
    <div
      className={`drishya-auth-panel ${className}`}
      style={{
        background: 'linear-gradient(180deg, #27180E 0%, #1A0E06 100%)',
        border: '1px solid var(--border-rich, rgba(201, 154, 60, 0.32))',
        borderRadius: '20px',
        padding: '2.2rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.75)',
        width: '100%',
        maxWidth: '440px',
      }}
    >
      {/* Mode Switch Tabs (Sign In / Create Account) */}
      <div
        role="tablist"
        aria-label="Authentication modes"
        style={{
          display: 'flex',
          borderBottom: '1px solid rgba(201, 154, 60, 0.2)',
          marginBottom: '1.8rem',
        }}
      >
        <button
          type="button"
          role="tab"
          id="tab-sign-in"
          aria-selected={mode === 'login'}
          onClick={() => handleModeSwitch('login')}
          style={{
            flex: 1,
            background: 'none',
            border: 'none',
            borderBottom: mode === 'login' ? '2.5px solid #F2C14E' : '2.5px solid transparent',
            padding: '0.75rem 0.5rem',
            fontFamily: isHindiOrMarathi ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)' : 'var(--font-display, Georgia, serif)',
            fontSize: isHindiOrMarathi ? '1.05rem' : '1.1rem',
            fontWeight: mode === 'login' ? '600' : '400',
            color: mode === 'login' ? '#FBF6EA' : 'var(--c-dust, #D8C7A3)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            outline: 'none',
          }}
        >
          {t('auth.sign_in')}
        </button>

        <button
          type="button"
          role="tab"
          id="tab-create-account"
          aria-selected={mode === 'register'}
          onClick={() => handleModeSwitch('register')}
          style={{
            flex: 1,
            background: 'none',
            border: 'none',
            borderBottom: mode === 'register' ? '2.5px solid #F2C14E' : '2.5px solid transparent',
            padding: '0.75rem 0.5rem',
            fontFamily: isHindiOrMarathi ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)' : 'var(--font-display, Georgia, serif)',
            fontSize: isHindiOrMarathi ? '1.05rem' : '1.1rem',
            fontWeight: mode === 'register' ? '600' : '400',
            color: mode === 'register' ? '#FBF6EA' : 'var(--c-dust, #D8C7A3)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            outline: 'none',
          }}
        >
          {t('auth.create_account')}
        </button>
      </div>

      {/* Calm Status / Feedback Messages */}
      {errorMsg && (
        <div
          role="alert"
          id="auth-error-message"
          style={{
            background: 'rgba(162, 74, 43, 0.22)',
            border: '1px solid rgba(162, 74, 43, 0.48)',
            color: '#F4D4CA',
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            fontSize: '0.88rem',
            marginBottom: '1.25rem',
            lineHeight: 1.4,
          }}
        >
          {errorMsg}
        </div>
      )}

      {successMsg && (
        <div
          role="status"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'rgba(94, 107, 56, 0.25)',
            border: '1px solid rgba(94, 107, 56, 0.5)',
            color: '#E0E8C7',
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            fontSize: '0.88rem',
            marginBottom: '1.25rem',
          }}
        >
          <CheckCircle2 size={16} />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        {/* Full Name Field (Register Mode Only) */}
        {mode === 'register' && (
          <div style={{ marginBottom: '1.25rem' }}>
            <label
              htmlFor="auth-name"
              style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: '500',
                color: 'var(--c-parchment, #F4EAD3)',
                marginBottom: '0.4rem',
                letterSpacing: '0.02em',
              }}
            >
              {t('auth.name')}
            </label>
            <input
              id="auth-name"
              name="name"
              type="text"
              autoComplete="name"
              required
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g. Ramesh Patil"
              style={{
                width: '100%',
                height: '48px',
                padding: '0 1rem',
                background: 'rgba(18, 10, 5, 0.85)',
                border: '1px solid rgba(201, 154, 60, 0.28)',
                borderRadius: '10px',
                color: '#FBF6EA',
                fontSize: '0.95rem',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#F2C14E')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(201, 154, 60, 0.28)')}
            />
          </div>
        )}

        {/* Email Field */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label
            htmlFor="auth-email"
            style={{
              display: 'block',
              fontSize: '0.85rem',
              fontWeight: '500',
              color: 'var(--c-parchment, #F4EAD3)',
              marginBottom: '0.4rem',
              letterSpacing: '0.02em',
            }}
          >
            {t('auth.email')}
          </label>
          <input
            id="auth-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={formData.email}
            onChange={handleInputChange}
            placeholder="farmer@example.com"
            style={{
              width: '100%',
              height: '48px',
              padding: '0 1rem',
              background: 'rgba(18, 10, 5, 0.85)',
              border: '1px solid rgba(201, 154, 60, 0.28)',
              borderRadius: '10px',
              color: '#FBF6EA',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-body, "Mukta", sans-serif)',
              outline: 'none',
              transition: 'border-color 0.2s',
            }}
            onFocus={(e) => (e.target.style.borderColor = '#F2C14E')}
            onBlur={(e) => (e.target.style.borderColor = 'rgba(201, 154, 60, 0.28)')}
          />
        </div>

        {/* Password Field */}
        <div style={{ marginBottom: mode === 'register' ? '1.25rem' : '1.8rem' }}>
          <label
            htmlFor="auth-password"
            style={{
              display: 'block',
              fontSize: '0.85rem',
              fontWeight: '500',
              color: 'var(--c-parchment, #F4EAD3)',
              marginBottom: '0.4rem',
              letterSpacing: '0.02em',
            }}
          >
            {t('auth.password')}
          </label>
          <div style={{ position: 'relative' }}>
            <input
              id="auth-password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
              required
              value={formData.password}
              onChange={handleInputChange}
              style={{
                width: '100%',
                height: '48px',
                padding: '0 3rem 0 1rem',
                background: 'rgba(18, 10, 5, 0.85)',
                border: '1px solid rgba(201, 154, 60, 0.28)',
                borderRadius: '10px',
                color: '#FBF6EA',
                fontSize: '0.95rem',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#F2C14E')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(201, 154, 60, 0.28)')}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? t('auth.hide_password') : t('auth.show_password')}
              style={{
                position: 'absolute',
                right: '0',
                top: '0',
                bottom: '0',
                width: '48px',
                background: 'transparent',
                border: 'none',
                color: 'var(--c-dust, #D8C7A3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        {/* Confirm Password Field (Register Mode Only) */}
        {mode === 'register' && (
          <div style={{ marginBottom: '1.8rem' }}>
            <label
              htmlFor="auth-confirm-password"
              style={{
                display: 'block',
                fontSize: '0.85rem',
                fontWeight: '500',
                color: 'var(--c-parchment, #F4EAD3)',
                marginBottom: '0.4rem',
                letterSpacing: '0.02em',
              }}
            >
              {t('auth.confirm_password')}
            </label>
            <input
              id="auth-confirm-password"
              name="confirmPassword"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleInputChange}
              style={{
                width: '100%',
                height: '48px',
                padding: '0 1rem',
                background: 'rgba(18, 10, 5, 0.85)',
                border: '1px solid rgba(201, 154, 60, 0.28)',
                borderRadius: '10px',
                color: '#FBF6EA',
                fontSize: '0.95rem',
                fontFamily: 'var(--font-body, "Mukta", sans-serif)',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#F2C14E')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(201, 154, 60, 0.28)')}
            />
          </div>
        )}

        {/* Primary Action Button (Minimum 48px touch target) */}
        <button
          type="submit"
          id="btn-auth-submit"
          disabled={loading}
          style={{
            width: '100%',
            minHeight: '50px',
            padding: '0.75rem 1.5rem',
            background: 'linear-gradient(135deg, #F2C14E 0%, #C99A3C 60%, #8A5A2B 100%)',
            border: 'none',
            borderRadius: '10px',
            color: '#140C07',
            fontFamily: isHindiOrMarathi ? 'var(--font-devanagari-display, "Tiro Devanagari Hindi", serif)' : 'var(--font-display, Georgia, serif)',
            fontSize: isHindiOrMarathi ? '1.05rem' : '1.1rem',
            fontWeight: '700',
            cursor: loading ? 'wait' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.6rem',
            boxShadow: '0 8px 20px rgba(201, 154, 60, 0.35)',
            transition: 'transform 0.15s ease, box-shadow 0.15s ease',
            opacity: loading ? 0.75 : 1,
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.98)')}
          onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1)')}
        >
          <span>
            {loading
              ? mode === 'register'
                ? t('auth.registering')
                : t('auth.signing_in')
              : mode === 'register'
              ? t('auth.create_account')
              : t('auth.sign_in')}
          </span>
          <ArrowRight size={18} />
        </button>
      </form>

      {/* Switch Helper Link */}
      <div style={{ marginTop: '1.4rem', textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => handleModeSwitch(mode === 'login' ? 'register' : 'login')}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--c-dust, #D8C7A3)',
            fontSize: '0.85rem',
            cursor: 'pointer',
            textDecoration: 'underline',
            textUnderlineOffset: '3px',
            opacity: 0.85,
          }}
        >
          {mode === 'login' ? t('auth.need_account_switch') : t('auth.have_account_switch')}
        </button>
      </div>

      {/* Field Privacy Assurance */}
      <p
        style={{
          marginTop: '1.25rem',
          fontSize: '0.74rem',
          color: 'var(--c-dusk, #6F5F52)',
          textAlign: 'center',
          lineHeight: 1.45,
        }}
      >
        {t('auth.privacy_note')}
      </p>
    </div>
  );
}
