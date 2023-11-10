import { useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router';

export default function Schema() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.pathname === '/schema') {
      navigate('/schema/image/point');
    }
  }, [location.pathname, navigate]);

  return <Outlet />;
}
