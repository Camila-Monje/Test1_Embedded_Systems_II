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
volatile uint32_t g_ui32MotorDuty = 0;   
volatile bool g_bLEDAState = false;      

void ConfigureUART(void);
void ConfigurePWM(void);
void UpdateOutputs(void);

void UARTIntHandler(void) {
    uint32_t ui32Status = MAP_UARTIntStatus(UART0_BASE, true);
    MAP_UARTIntClear(UART0_BASE, ui32Status);

    if (MAP_UARTCharsAvail(UART0_BASE)) {
        uint8_t cChar = MAP_UARTCharGetNonBlocking(UART0_BASE);
        
        if (cChar >= 'a' && cChar <= 'z') {
            cChar -= 32; 
        }
        
        switch(cChar) {
            case '0':  
                g_ui8Command = '0';
                g_ui32MotorDuty = 3750;    
                break;

            case '1':  
                g_ui8Command = '1';
                g_ui32MotorDuty = 2500;   
                break;

            case '2':  
                g_ui8Command = '2';
                g_ui32MotorDuty = 0;      
                g_bLEDAState = true;      
                break;


            case '3':  
                g_ui8Command = '3';
                g_ui32MotorDuty = 2500;   
                g_bLEDAState = false;    
                break;

            default:
                g_ui8Command = 0;
                g_ui32MotorDuty = 0;
                g_bLEDAState = false;
                break;
        }
        UpdateOutputs();
    }
}

void UpdateOutputs(void) {
    MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_0, g_ui32MotorDuty);  
    MAP_PWMOutputState(PWM0_BASE, PWM_OUT_0_BIT, true);
    MAP_PWMPulseWidthSet(PWM0_BASE, PWM_OUT_3, g_bLEDAState ? 1 : 0);  
    MAP_PWMOutputState(PWM0_BASE, PWM_OUT_3_BIT, true);
}

void ConfigurePWM(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    
    MAP_GPIOPinConfigure(GPIO_PF1_M0PWM1);  
    MAP_GPIOPinConfigure(GPIO_PF3_M0PWM3);  
    
    MAP_GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1 | GPIO_PIN_3);
    
    MAP_SysCtlPWMClockSet(SYSCTL_PWMDIV_8);
    uint32_t ui32PWMClock = g_ui32SysClock / 8;
    uint32_t ui32PWMPeriod = ui32PWMClock / 5000;  
    
    MAP_PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN);
    MAP_PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, ui32PWMPeriod);
    
    MAP_PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_DOWN);
    MAP_PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, ui32PWMPeriod);
    
    MAP_PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    MAP_PWMGenEnable(PWM0_BASE, PWM_GEN_1);
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
    g_ui32MotorDuty = 0;

    ConfigurePWM();
    ConfigureUART();

    MAP_IntMasterEnable();
    
    UpdateOutputs();
    
    while(1) {
        __asm(" WFI"); 
    }
}
