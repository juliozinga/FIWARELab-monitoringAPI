# coding: utf-8
from sqlalchemy import Column, DateTime, Float, String, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Host(Base):
    __tablename__ = 'host'

    entityId = Column(String(64), primary_key=True, nullable=False)
    region = Column(String(16), primary_key=True, nullable=False)
    host_name = Column(String(32), nullable=False)
    role = Column(String(16), nullable=False)
    aggregationType = Column(String(8), primary_key=True, nullable=False)
    timestampId = Column(DateTime, primary_key=True, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    avg_usedMemPct = Column(Float, nullable=False, server_default=text("'0'"))
    avg_freeSpacePct = Column(Float, nullable=False, server_default=text("'0'"))
    avg_cpuLoadPct = Column(Float, nullable=False, server_default=text("'0'"))
    host_id = Column(String(16), nullable=False)
    sysUptime = Column(Float, nullable=False, server_default=text("'0'"))


class HostService(Base):
    __tablename__ = 'host_service'

    entityId = Column(String(64), primary_key=True, nullable=False)
    region = Column(String(32), primary_key=True, nullable=False)
    entityType = Column(String(32), primary_key=True, nullable=False)
    serviceType = Column(String(32), primary_key=True, nullable=False)
    aggregationType = Column(String(8), primary_key=True, nullable=False)
    timestampId = Column(DateTime, primary_key=True, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    avg_Uptime = Column(Float, nullable=False, server_default=text("'0'"))


class Region(Base):
    __tablename__ = 'region'

    entityId = Column(String(16), primary_key=True, nullable=False)
    entityType = Column(String(16), nullable=False)
    aggregationType = Column(String(8), primary_key=True, nullable=False)
    timestampId = Column(DateTime, primary_key=True, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    avg_ram_used = Column(Float, nullable=False, server_default=text("'0'"))
    avg_ram_tot = Column(Float, nullable=False, server_default=text("'0'"))
    avg_core_enabled = Column(Float, nullable=False, server_default=text("'0'"))
    avg_core_used = Column(Float, nullable=False, server_default=text("'0'"))
    avg_core_tot = Column(Float, nullable=False, server_default=text("'0'"))
    avg_hd_used = Column(Float, nullable=False, server_default=text("'0'"))
    avg_hd_tot = Column(Float, nullable=False, server_default=text("'0'"))
    avg_vm_tot = Column(Float, nullable=False, server_default=text("'0'"))


class Vm(Base):
    __tablename__ = 'vm'

    entityId = Column(String(64), primary_key=True, nullable=False)
    region = Column(String(16), primary_key=True, nullable=False)
    entityType = Column(String(16), nullable=False)
    aggregationType = Column(String(8), primary_key=True, nullable=False)
    timestampId = Column(DateTime, primary_key=True, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    avg_usedMemPct = Column(Float, nullable=False, server_default=text("'0'"))
    avg_freeSpacePct = Column(Float, nullable=False, server_default=text("'0'"))
    avg_cpuLoadPct = Column(Float, nullable=False, server_default=text("'0'"))
    host_name = Column(String(32), nullable=False)
    sysUptime = Column(Float, nullable=False, server_default=text("'0'"))
