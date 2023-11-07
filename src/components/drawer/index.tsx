import clsx from 'clsx';
import { cloneElement, isValidElement, useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router';

export type DrawerProps = React.PropsWithChildren<{
  open?: boolean;
  width?: string;
  content?: React.ReactNode;
  onClose?: () => void;
}>;

export function Drawer({ children, open: propsOpen, width, content }: DrawerProps) {
  const [open, setOpen] = useState(!!propsOpen);
  const location = useLocation();

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setOpen(false);
    }
  };

  const trigger = isValidElement(children) ? (
    cloneElement(children as React.ReactElement, { onClick: handleOpen })
  ) : (
    <button onClick={handleOpen}>{children}</button>
  );

  useEffect(() => {
    setOpen(false);
  }, [location]);

  const contentStyle = useMemo(
    () => ({
      width,
    }),
    [width],
  );

  return (
    <>
      {trigger}
      <div
        className={clsx(
          'fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-50 transition-opacity duration-300 ease-in-out',
          {
            'opacity-100 pointer-events-auto': open,
            'opacity-0 pointer-events-none': !open,
          },
        )}
        onClick={handleClose}
      >
        <div
          style={contentStyle}
          className={clsx(
            `z-51 bg-white p-4 transition-transform duration-300 ease-in-out transform overflow-auto h-full`,
            {
              'translate-x-0': open,
              '-translate-x-full': !open,
            },
          )}
        >
          {content}
        </div>
      </div>
    </>
  );
}
