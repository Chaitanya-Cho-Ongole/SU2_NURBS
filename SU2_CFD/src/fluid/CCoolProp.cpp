/*!
 * \file CCoolProp.cpp
 * \brief Source of the fluid model from CoolProp.
 * \author P. Yan, G. Gori, A. Guardone
 * \version 8.0.1 "Harrier"
 *
 * SU2 Project Website: https://su2code.github.io
 *
 * The SU2 Project is maintained by the SU2 Foundation
 * (http://su2foundation.org)
 *
 * Copyright 2012-2024, SU2 Contributors (cf. AUTHORS.md)
 *
 * SU2 is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * SU2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with SU2. If not, see <http://www.gnu.org/licenses/>.
 */

 #include "../../include/fluid/CCoolProp.hpp"

 #ifdef USE_COOLPROP
 #include "AbstractState.h"
 #include "CoolProp.h"
 
 CCoolProp::CCoolProp(const string &fluidname) : CFluidModel() {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::CCoolProp"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::CCoolProp"<<std::endl;
   }
   counter++; 
   fluid_entity = std::unique_ptr<CoolProp::AbstractState>(CoolProp::AbstractState::factory("HEOS", fluidname));
   Gas_Constant = fluid_entity->gas_constant() / fluid_entity->molar_mass();
   Pressure_Critical = fluid_entity->p_critical();
   Temperature_Critical = fluid_entity->T_critical();
   acentric_factor = fluid_entity->acentric_factor();
 }
 
 CCoolProp::~CCoolProp() {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::~CCoolProp"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::~CCoolProp"<<std::endl;
   }
   counter++; 
 }
 
 void CCoolProp::SetTDState_rhoe(su2double rho, su2double e) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_rhoe"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_rhoe"<<std::endl;
   }
   counter++; 
   Density = rho;
   StaticEnergy = e;
   fluid_entity->update(CoolProp::DmassUmass_INPUTS, Density, StaticEnergy);
   Cp = fluid_entity->cpmass();
   Cv = fluid_entity->cvmass();
   Gamma = Cp / Cv;
   Pressure = fluid_entity->p();
   Temperature = fluid_entity->T();
   Entropy = fluid_entity->smass();
   dPdrho_e = fluid_entity->first_partial_deriv(CoolProp::iP, CoolProp::iDmass, CoolProp::iUmass);
   dPde_rho = fluid_entity->first_partial_deriv(CoolProp::iP, CoolProp::iUmass, CoolProp::iDmass);
   dTdrho_e = fluid_entity->first_partial_deriv(CoolProp::iT, CoolProp::iDmass, CoolProp::iUmass);
   dTde_rho = fluid_entity->first_partial_deriv(CoolProp::iT, CoolProp::iUmass, CoolProp::iDmass);
   if (fluid_entity->phase() == CoolProp::iphase_twophase) {
     // impose gas phase
     Temperature = Temperature + 0.1;
     CheckPressure(Pressure);
     CheckTemperature(Temperature);
     fluid_entity->update(CoolProp::PT_INPUTS, Pressure, Temperature);
     SoundSpeed2 = pow(fluid_entity->speed_sound(), 2);
   } else {
     SoundSpeed2 = pow(fluid_entity->speed_sound(), 2);
   }
 }
 
 void CCoolProp::SetTDState_PT(su2double P, su2double T) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_PT"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_PT"<<std::endl;
   }
   counter++; 
   CheckPressure(P);
   CheckTemperature(T);
   fluid_entity->update(CoolProp::PT_INPUTS, P, T);
   su2double rho = fluid_entity->rhomass();
   su2double e = fluid_entity->umass();
   SetTDState_rhoe(rho, e);
 }
 
 void CCoolProp::SetTDState_Prho(su2double P, su2double rho) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_Prho"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_Prho"<<std::endl;
   }
   counter++; 
   CheckPressure(P);
   fluid_entity->update(CoolProp::DmassP_INPUTS, rho, P);
   su2double e = fluid_entity->umass();
   SetTDState_rhoe(rho, e);
 }
 
 void CCoolProp::SetEnergy_Prho(su2double P, su2double rho) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetEnergy_Prho"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetEnergy_Prho"<<std::endl;
   }
   counter++; 
   CheckPressure(P);
   fluid_entity->update(CoolProp::DmassP_INPUTS, rho, P);
   StaticEnergy = fluid_entity->umass();
 }
 
 void CCoolProp::SetTDState_hs(su2double h, su2double s) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_hs"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_hs"<<std::endl;
   }
   counter++; 
   fluid_entity->update(CoolProp::HmassSmass_INPUTS, h, s);
   su2double rho = fluid_entity->rhomass();
   su2double e = fluid_entity->umass();
   SetTDState_rhoe(rho, e);
 }
 
 void CCoolProp::SetTDState_Ps(su2double P, su2double s) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_Ps"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_Ps"<<std::endl;
   }
   counter++; 
   CheckPressure(P);
   fluid_entity->update(CoolProp::PSmass_INPUTS, P, s);
   su2double rho = fluid_entity->rhomass();
   su2double e = fluid_entity->umass();
   SetTDState_rhoe(rho, e);
 }
 
 void CCoolProp::SetTDState_rhoT(su2double rho, su2double T) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_rhoT"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::SetTDState_rhoT"<<std::endl;
   }
   counter++; 
   fluid_entity->update(CoolProp::DmassT_INPUTS, rho, T);
   su2double e = fluid_entity->umass();
   SetTDState_rhoe(rho, e);
 }
 
 void CCoolProp::ComputeDerivativeNRBC_Prho(su2double P, su2double rho) {
   static int counter=0;
   if (counter==0){
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::ComputeDerivativeNRBC_Prho"<<std::endl;
   }
   
   if (counter==1){
     std::cout<<"REPEATED EVALS"<<std::endl;
     std::cout<<"FILE:SU2_CFD/src/fluid/CCoolProp.cpp"<<std::endl;
     std::cout<<"FUNCTION:CCoolProp::ComputeDerivativeNRBC_Prho"<<std::endl;
   }
   counter++; 
   SetTDState_Prho(P, rho);
   dhdrho_P = fluid_entity->first_partial_deriv(CoolProp::iHmass, CoolProp::iDmass, CoolProp::iP);
   dhdP_rho = fluid_entity->first_partial_deriv(CoolProp::iHmass, CoolProp::iP, CoolProp::iDmass);
   dsdP_rho = fluid_entity->first_partial_deriv(CoolProp::iSmass, CoolProp::iP, CoolProp::iDmass);
   dsdrho_P = fluid_entity->first_partial_deriv(CoolProp::iSmass, CoolProp::iDmass, CoolProp::iP);
 }
 
 #else
 CCoolProp::CCoolProp(const string& fluidname) {
   SU2_MPI::Error(
       "SU2 was not compiled with CoolProp (-Denable-coolprop=true). Note that CoolProp cannot be used with directdiff "
       "or autodiff",
       CURRENT_FUNCTION);
 }
 #endif