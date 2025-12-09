import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { HomeScreen } from '../screens/HomeScreen';
import { ReportDetailsScreen } from '../screens/ReportDetailsScreen';
import { CameraCaptureScreen } from '../screens/CameraCaptureScreen';

export type RootStackParamList = {
  Home: undefined;
  ReportDetails: { reportId: string };
  CameraCapture: { reportId: string };
};

const Stack = createStackNavigator<RootStackParamList>();

export const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#2196F3'
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold'
          }
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{
            title: 'RelatoRecibo',
            headerShown: false
          }}
        />

        <Stack.Screen
          name="ReportDetails"
          component={ReportDetailsScreen}
          options={{
            title: 'Detalhes do Relatório'
          }}
        />

        <Stack.Screen
          name="CameraCapture"
          component={CameraCaptureScreen}
          options={{
            title: 'Capturar Recibo',
            headerShown: false
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};
