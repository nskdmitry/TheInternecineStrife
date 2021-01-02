using System;
using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model.War.Battle
{
  public enum WeaponClass
  {
    Malee,
    Range
  }

  public class BattleFormation
  {
    public const float WIDE_OF_GROUND = 100;
    public const float ONE_STRIKE = 0.1f;
    public const float FEARY_DEFEATS = 0.1f;
    public const float EXTERMINATE_DEFEATS = 0.7f;
    public const float SURRENDER_DEFEATS = 0.5f;

    // Constants of Squid
    public int ID { get; set; }
    public Army Side { get; set; }

    // Update by battle process
    //
    public float DistanceToCenter { get; set; } // Notifiable
    public int Columns { get; set; } // Notifiable
    public int Rows { get; set; } // Notifiable
    public int Soldiers { get; set; } // Notifiable
    public WeaponClass Using { get; set; } // Notifiable
    public int MaleeResource { get; set; } // Notifiable
    public int RangeResource { get; set; } // Notifiable
    public float Energy { get; set; } // Notifiable
    public FormationVector V { get; set; } // Notifiable
    public bool BlendMalee { get; set; } // Notifiable
    public bool Ranger { get; set; } // Notifiable
    public bool FireOnMarsh { get; set; } // Notifiable

    // Damage (Infirmary)
    public int Killed { get; set; }
    public List<int> Woundeds { get; set; }

    // Set by owner before battle or in battle
    //
    public float Density { get; set; } // Notifiable, Controllable
    public float RangeAttackDistance { get; set; } // Controllable
    public float MaleeAttackDistance { get; set; } // Controllable

    // Facade
    //
    public SoldierProfile Class { get { return Side.Class; } }
    public Formation Organization { get { return Side.Formation; } }
    public float Speed { get { return Side.Class.Speed; } }
    public Weapon Malee { get { return Side.Class.Malee; } }
    public Weapon Range { get { return Side.Class.Range; } }
    
    public float Length { get { return Columns* Density; } }

    public bool CanFigth
    {
      get
      {
        var canMalee = Using == WeaponClass.Malee && MaleeResource > 0;
        var canRange = Using == WeaponClass.Range && RangeResource > 0;
        return Soldiers > 0 &&
          Energy > ONE_STRIKE &&
          (canMalee || canRange);
      }
    }

    public BattleFormation(int id, Army forces, bool fromLeft)
    {
      ID = id;
      Side = forces;

      Soldiers = forces.Strength;
      Energy = forces.Energy;
      Using = Range != null ? WeaponClass.Range : WeaponClass.Malee;

      MaleeResource = Organization.MaleeResource;
      RangeResource = Organization.RangeResource;
      DistanceToCenter = fromLeft ? -WIDE_OF_GROUND/2 : WIDE_OF_GROUND/2;
      RangeAttackDistance = (Range.Near + Range.Far) / 2;
      MaleeAttackDistance = Malee.Far + Speed;
      Reorganize(this);
    }

    /// Перегруппировка войск.
    /// Устанавливает параметры согласно ТТХ (тактико-техническим характеристикам), установленным пользователем
    public void Reorganize(object sender)
    {
      var form = Organization;
      BlendMalee = !form.NoBlendMalee;
      Ranger = form.Ranger;
      FireOnMarsh = form.FireOnMarsh;
      Columns = form.Columns;
      Density = form.Density;
      RangeAttackDistance = form.RangeAttackDistance;
      MaleeAttackDistance = form.MaleeAttackDistance;
      Rows = (int)Math.Ceiling((float)Soldiers / Columns);
    }
  }
}
