import { useMediaQuery } from 'react-responsive';

export function useResponse() {
  const isXXSmallScreen = useMediaQuery({
    maxWidth: 600,
  });
  const isXSmallScreen = useMediaQuery({
    minWidth: 601,
    maxWidth: 800,
  });
  const isSmallScreen = useMediaQuery({
    minWidth: 801,
    maxWidth: 1200,
  });
  const isRegularScreen = useMediaQuery({
    minWidth: 1201,
    maxWidth: 1600,
  });
  const isLargeScreen = useMediaQuery({
    minWidth: 1601,
    maxWidth: 2500,
  });
  const isXLargeScreen = useMediaQuery({
    minWidth: 2501,
  });

  if (isXXSmallScreen) {
    return 'xxsmall';
  } else if (isXSmallScreen) {
    return 'xsmall';
  } else if (isSmallScreen) {
    return 'small';
  } else if (isRegularScreen) {
    return 'regular';
  } else if (isLargeScreen) {
    return 'large';
  } else if (isXLargeScreen) {
    return 'xlarge';
  }

  return 'regular';
}
