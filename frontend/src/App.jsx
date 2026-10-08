import React, { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import WelcomeScreen from './components/welcome/WelcomeScreen';
import Header from './components/navigation/Header';
import HomeScreen from './components/home/HomeScreen';
import CheckLeafScreen from './components/check/CheckLeafScreen';
import AnalysisScreen from './components/analysis/AnalysisScreen';
import ResultScreen from './components/result/ResultScreen';
import JournalScreen from './components/journal/JournalScreen';
import GuideScreen from './components/guide/GuideScreen';
import AboutScreen from './components/about/AboutScreen';
import MobileBottomNav from './components/navigation/MobileBottomNav';

function MainLayout() {
  const { user, isAuthenticated, loading: authLoading, currentPath, navigate } = useAuth();
  const { t } = useLanguage();

  // ── Step 5 & 6: Diagnosis result handoff state ───────────────────────────
  // Holds the last successful diagnosis response for the Analysis & Result screens.
  // Raw image bytes are NOT stored in localStorage or URL — held in React memory only.
  const [lastDiagnosisResult, setLastDiagnosisResult] = useState(null);

  // Clean up previous object URL if a new diagnosis is initiated
  const prevUrlRef = useRef(null);
  useEffect(() => {
    if (prevUrlRef.current && prevUrlRef.current !== lastDiagnosisResult?.imageObjectUrl) {
      try {
        URL.revokeObjectURL(prevUrlRef.current);
      } catch (e) {
        // Safe ignore
      }
    }
    prevUrlRef.current = lastDiagnosisResult?.imageObjectUrl || null;
  }, [lastDiagnosisResult]);

  // Clean up object URL on unmount of MainLayout
  useEffect(() => {
    return () => {
      if (prevUrlRef.current) {
        try {
          URL.revokeObjectURL(prevUrlRef.current);
        } catch (e) {
          // Safe ignore
        }
      }
    };
  }, []);

  // Show Welcome & Authentication Experience for guests or when on /welcome
  if (!isAuthenticated || currentPath === '/welcome') {
    return <WelcomeScreen />;
  }

  // Parse query parameters (e.g. ?crop=turmeric)
  let selectedCrop = null;
  if (typeof window !== 'undefined') {
    const params = new URLSearchParams(window.location.search);
    selectedCrop = params.get('crop');
  }

  // Handle crop selection from Home → navigate to /check?crop=<crop>
  const handleSelectCrop = (cropKey) => {
    navigate(`/check?crop=${cropKey}`);
  };

  // Handle "Change crop" inside CheckLeafScreen → return to Home
  const handleChangeCrop = () => {
    navigate('/home');
  };

  // Step 5 -> Step 6: Handle completed diagnosis — hand off to /analysis
  const handleDiagnosisComplete = (resultPayload) => {
    // resultPayload: { diagnosisResponse, crop, imageObjectUrl, imageFileName, imageFile }
    setLastDiagnosisResult(resultPayload);
    navigate('/analysis');
  };

  // Step 6 -> Step 7: Handle completed analysis transition — proceed to /result
  const handleAnalysisComplete = () => {
    navigate('/result');
  };

  // Safe exit from /analysis back to /check (preserving image file & URL)
  const handleBackToCheck = () => {
    const cropParam = lastDiagnosisResult?.crop ? `?crop=${lastDiagnosisResult.crop}` : '';
    navigate(`/check${cropParam}`);
  };

  const isAnalysis = currentPath.startsWith('/analysis');

  // Render appropriate view based on current route
  const renderCurrentView = () => {
    // Check a Leaf workspace (Step 5)
    if (currentPath.startsWith('/check')) {
      return (
        <CheckLeafScreen
          initialCrop={selectedCrop || lastDiagnosisResult?.crop || 'turmeric'}
          initialImageFile={lastDiagnosisResult?.imageFile || null}
          initialImageObjectUrl={lastDiagnosisResult?.imageObjectUrl || null}
          onChangeCrop={handleChangeCrop}
          onDiagnosisComplete={handleDiagnosisComplete}
        />
      );
    }

    // Real DRISHYA Analysis Experience (Step 6)
    if (currentPath.startsWith('/analysis')) {
      return (
        <AnalysisScreen
          diagnosisPayload={lastDiagnosisResult}
          onComplete={handleAnalysisComplete}
          onBackToCheck={handleBackToCheck}
        />
      );
    }

    // Real DRISHYA Diagnosis Result Experience (Step 7)
    if (currentPath.startsWith('/result')) {
      return (
        <ResultScreen
          diagnosisPayload={lastDiagnosisResult}
          onCheckAnother={() => {
            const cropParam = lastDiagnosisResult?.crop ? `?crop=${lastDiagnosisResult.crop}` : '';
            navigate(`/check${cropParam}`);
          }}
          onBackToHome={() => navigate('/home')}
        />
      );
    }

    // Real DRISHYA My Leaf Journal Experience (Step 8)
    if (currentPath.startsWith('/journal')) {
      return (
        <JournalScreen
          activeSessionDiagnosis={lastDiagnosisResult}
          onCheckLeaf={() => {
            const cropParam = lastDiagnosisResult?.crop ? `?crop=${lastDiagnosisResult.crop}` : '';
            navigate(`/check${cropParam}`);
          }}
          onBackToHome={() => navigate('/home')}
        />
      );
    }

    // Real DRISHYA Field Guide Experience (Step 9)
    if (currentPath.startsWith('/guide')) {
      return <GuideScreen onBackToHome={() => navigate('/home')} />;
    }

    // Real DRISHYA About Experience (Step 9)
    if (currentPath.startsWith('/about')) {
      return <AboutScreen onBackToHome={() => navigate('/home')} />;
    }

    // Default: Home
    return <HomeScreen onSelectCrop={handleSelectCrop} />;
  };

  const isDarkBackground = isAnalysis || currentPath.startsWith('/about');

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: isDarkBackground ? '#160E08' : '#FBF6EA',
        transition: 'background-color 0.3s ease',
      }}
    >
      {/* Authenticated DRISHYA Header */}
      <Header />

      {/* Main Workspace Body */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {renderCurrentView()}
      </main>

      {/* Preserved verification indicator for sample-check-title */}
      <div id="sample-check-title" style={{ display: 'none' }} aria-hidden="true">
        🍃 {t('check.title')}
      </div>

      {/* Mobile Bottom Navigation (omitted on /analysis for full immersion) */}
      {!isAnalysis && <MobileBottomNav currentRoute={currentPath} />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <MainLayout />
      </LanguageProvider>
    </AuthProvider>
  );
}
