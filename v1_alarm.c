#changes made from the rebase 
#Codigo C 
#include <stdint.h>
 #include <stdbool.h>
 #include "inc/hw_ints.h"
 #include "inc/hw_memmap.h"
 #include "driverlib/debug.h"
 #include "driverlib/gpio.h"
 #include "driverlib/interrupt.h"
 #include "driverlib/pin_map.h"
 #include "driverlib/rom.h"
 #include "driverlib/rom_map.h"
 #include "driverlib/sysctl.h"
 #include "driverlib/uart.h"
 #include "driverlib/pwm.h"
 
 uint32_t g_ui32SysClock;
 volatile uint8_t g_ui8Command = 0;
 volatile uint32_t g_ui32LED1Duty = 0;
 volatile uint32_t g_ui32LED2Duty = 0;
 volatile bool g_bLEDAState = false; 
 
 void ConfigureUART(void);
 void ConfigurePWM(void);
 void UpdateOutputs(void);
 void ButtonInterruptHandler(void);
 
 void ConfigureButton(void) {
     MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
     MAP_GPIOPinTypeGPIOInput(GPIO_PORTF_BASE, GPIO_PIN_4);
     
     MAP_GPIOIntTypeSet(GPIO_PORTF_BASE, GPIO_PIN_4, GPIO_FALLING_EDGE); 
     MAP_GPIOIntEnable(GPIO_PORTF_BASE, GPIO_PIN_4);  
     MAP_IntEnable(INT_GPIOF); 
 }
 
 void ButtonInterruptHandler(void) {
     uint32_t ui32Status = MAP_GPIOIntStatus(GPIO_PORTF_BASE, true);
     MAP_GPIOIntClear(GPIO_PORTF_BASE, ui32Status); 
 
     if (g_bLEDAState) {
         g_bLEDAState = false; 
     } else {
         g_bLEDAState = true; 
     }
 
     UpdateOutputs(); 
 }
 
 void UpdateOutputs(void) {
     MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_0, g_ui32LED1Duty);
     MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, g_ui32LED2Duty); 
     
     MAP_GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, g_bLEDAState ? GPIO_PIN_3 : 0); 
 }
 
 void ConfigurePWM(void) {
     MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
     MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
     
     MAP_GPIOPinConfigure(GPIO_PF0_M0PWM0); 
     MAP_GPIOPinConfigure(GPIO_PF1_M0PWM1);  
     
     MAP_GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_1);
     
     MAP_SysCtlPWMClockSet(SYSCTL_PWMDIV_8);
     uint32_t ui32PWMClock = g_ui32SysClock / 8;
     uint32_t ui32PWMPeriod = ui32PWMClock / 5000;  
 
     MAP_PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN);
     MAP_PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, ui32PWMPeriod);
     
     MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_0, 0);  
     MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, 0);  
 
     MAP_PWMOutputState(PWM0_BASE, PWM_OUT_0_BIT | PWM_OUT_1_BIT, true);
     MAP_PWMGenEnable(PWM0_BASE, PWM_GEN_0);
 }
 
 void ConfigureUART(void) {
     MAP_GPIOPinConfigure(GPIO_PA0_U0RX);
     MAP_GPIOPinConfigure(GPIO_PA1_U0TX);
     MAP_GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
     
     MAP_UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
                             (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));
     
     MAP_IntEnable(INT_UART0);
     MAP_UARTIntEnable(UART0_BASE, UART_INT_RX | UART_INT_RT);
     MAP_IntMasterEnable();
 }
 
 int main(void) {
     g_ui32SysClock = MAP_SysCtlClockFreqSet(
         SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | 
         SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240, 120000000);
 
     g_ui8Command = 0;
     g_ui32LED1Duty = 0;
     g_ui32LED2Duty = 0;
 
     ConfigurePWM();
     ConfigureUART();
     ConfigureButton(); 
     
     MAP_IntMasterEnable();
     
     UpdateOutputs();
     
     while(1) {
         __asm(" WFI"); 
     }
 }