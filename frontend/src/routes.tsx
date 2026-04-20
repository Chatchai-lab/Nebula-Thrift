import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { ProtectedLayout } from './components/ProtectedLayout';
import { ProtectedOnboarding } from './components/ProtectedOnboarding';

const Landing = lazy(() =>
  import('./pages/Landing').then(({ Landing }) => ({ default: Landing }))
);
const Dashboard = lazy(() =>
  import('./pages/Dashboard').then(({ Dashboard }) => ({ default: Dashboard }))
);
const Recommendations = lazy(() =>
  import('./pages/Recommendations').then(({ Recommendations }) => ({ default: Recommendations }))
);
const Simulator = lazy(() =>
  import('./pages/Resources').then(({ Resources }) => ({ default: Resources }))
);
const Login = lazy(() =>
  import('./pages/Login').then(({ Login }) => ({ default: Login }))
);
const Onboarding = lazy(() =>
  import('./pages/Onboarding').then(({ Onboarding }) => ({ default: Onboarding }))
);
const Settings = lazy(() =>
  import('./pages/Settings').then(({ Settings }) => ({ default: Settings }))
);
const Register = lazy(() =>
  import('./pages/Register').then(({ Register }) => ({ default: Register }))
);

function PageLoader() {
  return <div className="min-h-screen bg-background" />;
}

function withSuspense(Component: React.ComponentType) {
  return function SuspenseWrapper() {
    return (
      <Suspense fallback={<PageLoader />}>
        <Component />
      </Suspense>
    );
  };
}

export const router = createBrowserRouter([
  {
    path: '/',
    children: [
      {
        index: true,
        Component: withSuspense(Landing),
      },
      {
        path: 'dashboard',
        Component: ProtectedLayout,
        children: [{ index: true, Component: withSuspense(Dashboard) }],
      },
      {
        path: 'recommendations',
        Component: ProtectedLayout,
        children: [{ index: true, Component: withSuspense(Recommendations) }],
      },
      {
        path: 'simulator',
        Component: ProtectedLayout,
        children: [{ index: true, Component: withSuspense(Simulator) }],
      },
      {
        path: 'settings',
        Component: ProtectedLayout,
        children: [{ index: true, Component: withSuspense(Settings) }],
      },
      {
        path: 'login',
        Component: withSuspense(Login),
      },
      {
        path: 'register',
        Component: withSuspense(Register),
      },
      {
        path: 'onboarding',
        Component: ProtectedOnboarding,
        children: [{ index: true, Component: withSuspense(Onboarding) }],
      },
    ],
  },
]);
