import React from 'react';
import { CheckOutlined } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';

import Separator from '../Separator';
import { IconWrapper, StepItemInner, StepItemWrapper } from './style';

export interface StepData {
  title: string;
  value: any;
  isFinished?: boolean;
}

interface StepItemProps {
  isEnd: boolean;
  active?: boolean;
  index: number;
  step: StepData;
  currentStep: StepData;
  onClick: (e: React.MouseEvent) => void;
}

const StepItem = ({ step, index, isEnd, onClick, active }: StepItemProps) => {
  return (
    <StepItemWrapper justify="space-around" items="center">
      <StepItemInner gap=".5rem" items="center" flex onClick={onClick}>
        <IconWrapper flex items="center" justify="center" active={active} finished={step.isFinished}>
          {step.isFinished ? <CheckOutlined /> : index + 1}
        </IconWrapper>
        <span> {step.title} </span>
      </StepItemInner>
      {!isEnd && <Separator />}
    </StepItemWrapper>
  );
};

interface StepProps {
  steps: StepData[];
  currentStep: any;
  onNext: (step: StepData, lastStep: StepData) => void;
  onPrev: (step: StepData, lastStep: StepData) => void;
}

export default function Step({ steps, currentStep, onNext, onPrev }: StepProps) {
  const currentStepIndex = steps.findIndex((step) => step.value === currentStep);
  const currentStepData = steps[currentStepIndex];

  const handleOnClick = (step: StepData, index: number) => {
    if (index > currentStepIndex && typeof onNext === 'function') {
      onNext(step, currentStepData);
    }

    if (index < currentStepIndex && typeof onPrev === 'function') {
      onPrev(step, currentStepData);
    }
  };

  return (
    <FlexLayout items="center" justify="flex-start">
      {steps.map((step, index) => {
        return (
          <StepItem
            key={step.value}
            active={currentStepIndex === index}
            onClick={() => handleOnClick(step, index)}
            step={step}
            isEnd={index === steps.length - 1}
            index={index}
            currentStep={currentStepData}
          />
        );
      })}
    </FlexLayout>
  );
}
