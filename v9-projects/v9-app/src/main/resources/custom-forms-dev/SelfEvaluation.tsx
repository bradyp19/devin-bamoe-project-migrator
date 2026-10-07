import React, { useCallback, useEffect, useState } from 'react';
import { TextInput, FormGroup } from '@patternfly/react-core';

const Form__SelfEvaluation: React.FC<any> = (props: any) => {
	const [formApi, setFormApi] = useState<any>();
	const [employee, set__employee] = useState<string>('');
	const [initiator, set__initiator] = useState<string>('');
	const [performance, set__performance] = useState<number>();
	const [reason, set__reason] = useState<string>('');

	const setFormData = (data) => {
		if (!data) {
			return;
		}
		set__employee(data?.employee ?? '');
		set__initiator(data?.initiator ?? '');
		set__performance(data?.performance);
		set__reason(data?.reason ?? '');
	};

	const getFormData = useCallback(() => {
		const formData: any = {};
		formData.employee = employee;
		formData.initiator = initiator;
		formData.performance = performance;
		formData.reason = reason;
		return formData;
	}, [employee, initiator, performance, reason]);

	const validateForm = useCallback(() => {}, []);
	const afterSubmit = useCallback((result) => {}, []);

	useEffect(() => {
		if (formApi) {
			formApi.beforeSubmit = () => validateForm();
			formApi.afterSubmit = (result) => afterSubmit(result);
			formApi.getFormData = () => getFormData();
		}
	}, [getFormData, validateForm, afterSubmit]);

	useEffect(() => {
		const api = window.Form.openForm({
			onOpen: (data, context) => {
				setFormData(data);
			},
		});
		setFormApi(api);
	}, []);

	return (
		<div className={'pf-v5-c-form'}>
			<FormGroup
				fieldId={'uniforms-0000-0000'}
				label={'Employee'}
				isRequired={false}>
				<TextInput
					name={'employee'}
					id={'uniforms-0000-0000'}
					isDisabled={false}
					placeholder={''}
					type={'text'}
					value={employee}
					onChange={(e, newValue) => set__employee(newValue)}
				/>
			</FormGroup>
			<FormGroup
				fieldId={'uniforms-0000-0001'}
				label={'Initiator'}
				isRequired={false}>
				<TextInput
					name={'initiator'}
					id={'uniforms-0000-0001'}
					isDisabled={false}
					placeholder={''}
					type={'text'}
					value={initiator}
					onChange={(e, newValue) => set__initiator(newValue)}
				/>
			</FormGroup>
			<FormGroup
				fieldId={'uniforms-0000-0003'}
				label={'Performance'}
				isRequired={false}>
				<TextInput
					type={'number'}
					name={'performance'}
					isDisabled={false}
					id={'uniforms-0000-0003'}
					placeholder={''}
					step={1}
					value={performance}
					onChange={(e, newValue) => set__performance(Number(newValue))}
				/>
			</FormGroup>
			<FormGroup
				fieldId={'uniforms-0000-0004'}
				label={'Reason'}
				isRequired={false}>
				<TextInput
					name={'reason'}
					id={'uniforms-0000-0004'}
					isDisabled={false}
					placeholder={''}
					type={'text'}
					value={reason}
					onChange={(e, newValue) => set__reason(newValue)}
				/>
			</FormGroup>
		</div>
	);
};

export default Form__SelfEvaluation;
